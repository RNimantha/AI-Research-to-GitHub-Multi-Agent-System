#!/usr/bin/env python3
"""Seed a list of starter topics for testing."""

SEED_TOPICS = [
    "Model Context Protocol (MCP) for AI Agents",
    "LangGraph multi-agent workflow orchestration",
    "Structured outputs in LLMs using JSON schema",
    "Multimodal RAG with vision-language models",
    "AI agent memory architectures and persistence",
    "Fine-tuning small LLMs with LoRA and QLoRA",
    "Speculative decoding for faster LLM inference",
    "Tool use and function calling in production AI systems",
    "Agentic coding assistants: architecture and evaluation",
    "Synthetic data generation for LLM fine-tuning",
]

if __name__ == "__main__":
    print("Available starter topics:\n")
    for i, topic in enumerate(SEED_TOPICS, 1):
        print(f"  {i:2}. {topic}")
    print(f"\nRun with: python scripts/test_single_topic.py --topic \"<topic>\"")
