# agentspring/tools/agents_catalog.py
from __future__ import annotations
from . import tool
from .delegate import delegate_agent

# Minimal named-agent catalog (extend as you like)
CATALOG: dict[str, str] = {
    "researcher": (
        "You are a careful web researcher. Always cite URLs. "
        "Use http_get for retrieval, summarize objectively."
    ),
    "calculator": (
        "You are a precise calculator. Use math_eval for any arithmetic. "
        "Return only the final number and a short note."
    ),
    "summarizer": (
        "You condense content into crisp bullet points with key facts first. "
        "Keep 3–6 bullets max."
    ),
}

@tool(
    "call_named_agent",
    "Call a named sub-agent from the local catalog and return its result.",
    parameters={
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "researcher|calculator|summarizer"},
            "task": {"type": "string"},
            "provider": {"type": "string"},
        },
        "required": ["name", "task"]
    },
)
async def call_named_agent(name: str, task: str, provider: str | None = None) -> dict:
    sys_prompt = CATALOG.get(name, "")
    return await delegate_agent(
        prompt=(f"{sys_prompt}\n\nTask:\n{task}" if sys_prompt else task),
        provider=provider
    )

