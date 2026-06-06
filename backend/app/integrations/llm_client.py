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
