import json
import time
from typing import Any

from backend.app.config import settings


ANTHROPIC_PRICING: dict[str, dict[str, float]] = {
    "claude-3-5-sonnet-latest": {"input": 3.0, "output": 15.0},
    "claude-3-5-haiku-latest": {"input": 0.80, "output": 4.0},
    "claude-opus-4-5": {"input": 15.0, "output": 75.0},
    "claude-sonnet-4-5": {"input": 3.0, "output": 15.0},
    "claude-3-opus-20240229": {"input": 15.0, "output": 75.0},
}

OPENAI_PRICING: dict[str, dict[str, float]] = {
    "gpt-4o": {"input": 2.50, "output": 10.0},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4-turbo": {"input": 10.0, "output": 30.0},
    "gpt-4": {"input": 30.0, "output": 60.0},
    "o1": {"input": 15.0, "output": 60.0},
    "o1-mini": {"input": 3.0, "output": 12.0},
    "o3-mini": {"input": 1.10, "output": 4.40},
}

_DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"


def _estimate_cost(provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
    table = ANTHROPIC_PRICING if provider == "anthropic" else OPENAI_PRICING
    pricing = table.get(model, {"input": 3.0, "output": 15.0})
    return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000


class LLMClient:
    """Thin wrapper around Anthropic and OpenAI clients with usage tracking."""

    def __init__(self, model: str | None = None, provider: str | None = None) -> None:
        self._provider = provider or settings.default_llm_provider
        self.model = model or self._default_model()
        self._client = self._init_client()

    def _default_model(self) -> str:
        if self._provider == "openai":
            m = settings.default_llm_model
            if m.startswith(("gpt-", "o1", "o3")):
                return m
            return _DEFAULT_OPENAI_MODEL
        return settings.default_llm_model

    def _init_client(self) -> Any:
        if self._provider == "anthropic":
            if not settings.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY is required when provider=anthropic")
            import anthropic
            return anthropic.Anthropic(api_key=settings.anthropic_api_key)
        if self._provider == "openai":
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY is required when provider=openai")
            from openai import OpenAI
            return OpenAI(api_key=settings.openai_api_key)
        raise ValueError(f"Unsupported LLM provider: {self._provider!r}. Use 'anthropic' or 'openai'.")

    def complete(
        self,
        system: str,
        user: str,
        max_tokens: int = 4096,
        temperature: float = 0.2,
        json_mode: bool = False,
    ) -> dict[str, Any]:
        """Call the LLM and return response with usage metadata."""
        start = time.time()

        if json_mode:
            system = system + "\n\nReturn valid JSON only. No markdown code blocks, no preamble."
            # Responses API requires the word "json" in input, not just instructions
            if self._provider == "openai":
                user = user + "\n\nRespond with valid JSON only."

        if self._provider == "anthropic":
            raw = self._complete_anthropic(system, user, max_tokens, temperature, json_mode)
        else:
            raw = self._complete_openai(system, user, max_tokens, temperature, json_mode)

        result: dict[str, Any] = {
            "content": raw["content"],
            "model": self.model,
            "provider": self._provider,
            "input_tokens": raw["input_tokens"],
            "output_tokens": raw["output_tokens"],
            "estimated_cost_usd": _estimate_cost(
                self._provider, self.model, raw["input_tokens"], raw["output_tokens"]
            ),
            "latency_ms": int((time.time() - start) * 1000),
        }

        if json_mode:
            result["parsed"] = json.loads(raw["content"])

        return result

    def _complete_anthropic(
        self, system: str, user: str, max_tokens: int, temperature: float, json_mode: bool
    ) -> dict[str, Any]:
        response = self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
            temperature=temperature,
        )
        return {
            "content": response.content[0].text,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        }

    def _complete_openai(
        self, system: str, user: str, max_tokens: int, temperature: float, json_mode: bool
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "instructions": system,
            "input": user,
            "max_output_tokens": max_tokens,
        }
        # o1/o3 models don't support temperature
        if not self.model.startswith(("o1", "o3")):
            kwargs["temperature"] = temperature
        if json_mode and not self.model.startswith(("o1", "o3")):
            kwargs["text"] = {"format": {"type": "json_object"}}

        response = self._client.responses.create(**kwargs)
        usage = response.usage
        return {
            "content": response.output_text,
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens,
        }

    def complete_json(self, system: str, user: str, max_tokens: int = 8192) -> dict[str, Any]:
        return self.complete(system=system, user=user, max_tokens=max_tokens, json_mode=True)

    def complete_with_tools(
        self,
        system: str,
        user: str,
        tools: list[dict[str, Any]],
        tool_executor: Any,
        max_tool_calls: int = 10,
        max_tokens: int = 8192,
    ) -> dict[str, Any]:
        """
        Agentic tool-use loop. Calls LLM, executes tool calls, feeds results back,
        repeats until LLM returns a final text response (stop_reason != tool_use).

        tool_executor: callable(tool_name, tool_input) -> str
        Returns: same shape as complete() but with extra "tool_calls_made" count.
        """
        start = time.time()
        total_input = 0
        total_output = 0
        tool_calls_made = 0

        if self._provider == "anthropic":
            content, input_tok, output_tok = self._tool_loop_anthropic(
                system, user, tools, tool_executor, max_tool_calls, max_tokens
            )
            total_input, total_output = input_tok, output_tok
            tool_calls_made = input_tok  # overwritten below
            content, total_input, total_output, tool_calls_made = content, input_tok, output_tok, tool_calls_made
        elif self._provider == "openai":
            content, total_input, total_output, tool_calls_made = self._tool_loop_openai(
                system, user, tools, tool_executor, max_tool_calls, max_tokens
            )
        else:
            raise ValueError(f"Unsupported provider: {self._provider}")

        return {
            "content": content,
            "model": self.model,
            "provider": self._provider,
            "input_tokens": total_input,
            "output_tokens": total_output,
            "estimated_cost_usd": _estimate_cost(self._provider, self.model, total_input, total_output),
            "latency_ms": int((time.time() - start) * 1000),
            "tool_calls_made": tool_calls_made,
        }

    def _tool_loop_anthropic(
        self,
        system: str,
        user: str,
        tools: list[dict[str, Any]],
        tool_executor: Any,
        max_tool_calls: int,
        max_tokens: int,
    ) -> tuple[str, int, int, int]:
        import anthropic

        anthropic_tools = []
        for t in tools:
            anthropic_tools.append({
                "name": t["name"],
                "description": t["description"],
                "input_schema": t["parameters"],
            })

        messages: list[dict[str, Any]] = [{"role": "user", "content": user}]
        total_input = 0
        total_output = 0
        tool_calls_made = 0
        final_text = ""

        for _ in range(max_tool_calls + 1):
            response = self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                tools=anthropic_tools,
                messages=messages,
                temperature=0.2,
            )
            total_input += response.usage.input_tokens
            total_output += response.usage.output_tokens

            if response.stop_reason == "end_turn":
                for block in response.content:
                    if hasattr(block, "text"):
                        final_text = block.text
                break

            if response.stop_reason == "tool_use":
                assistant_content = []
                tool_results = []

                for block in response.content:
                    if hasattr(block, "text"):
                        assistant_content.append({"type": "text", "text": block.text})
                    elif block.type == "tool_use":
                        assistant_content.append({
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input,
                        })
                        result = tool_executor(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(result),
                        })
                        tool_calls_made += 1

                messages.append({"role": "assistant", "content": assistant_content})
                messages.append({"role": "user", "content": tool_results})
            else:
                break

        return final_text, total_input, total_output, tool_calls_made

    def _tool_loop_openai(
        self,
        system: str,
        user: str,
        tools: list[dict[str, Any]],
        tool_executor: Any,
        max_tool_calls: int,
        max_tokens: int,
    ) -> tuple[str, int, int, int]:
        import json as _json

        openai_tools = [
            {
                "type": "function",
                "name": t["name"],
                "description": t["description"],
                "parameters": t["parameters"],
                "strict": False,
            }
            for t in tools
        ]

        total_input = 0
        total_output = 0
        tool_calls_made = 0
        final_text = ""

        # First call — use instructions + user input
        response = self._client.responses.create(
            model=self.model,
            instructions=system,
            input=user,
            tools=openai_tools,
            max_output_tokens=max_tokens,
            temperature=0.2,
        )
        total_input += response.usage.input_tokens
        total_output += response.usage.output_tokens

        for _ in range(max_tool_calls):
            pending_calls = [
                item for item in response.output
                if getattr(item, "type", None) == "function_call"
            ]

            if not pending_calls:
                final_text = response.output_text or ""
                break

            # Execute all tool calls, collect outputs
            tool_outputs: list[dict[str, Any]] = []
            for call in pending_calls:
                args = _json.loads(call.arguments) if isinstance(call.arguments, str) else call.arguments
                result = tool_executor(call.name, args)
                tool_outputs.append({
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": str(result),
                })
                tool_calls_made += 1

            # Continue from where we left off — previous_response_id threads context
            response = self._client.responses.create(
                model=self.model,
                previous_response_id=response.id,
                input=tool_outputs,
                tools=openai_tools,
                max_output_tokens=max_tokens,
                temperature=0.2,
            )
            total_input += response.usage.input_tokens
            total_output += response.usage.output_tokens
        else:
            # Hit max_tool_calls limit — take whatever text we have
            final_text = response.output_text or ""

        return final_text, total_input, total_output, tool_calls_made
