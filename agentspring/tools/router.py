# agentspring/tools/router.py
from __future__ import annotations
import re
from . import tool
from .agents_catalog import CATALOG
from .delegate import delegate_agent

ROUTES = [
    ("calculator", [r"\bcalc(ulate|ulation)?\b", r"\b(\d+\s*[\+\-\*/]\s*\d+)\b", r"\bmath\b"]),
    ("researcher", [r"\bhttp(s)?://", r"\bsource|cite|research|find\b"]),
    ("summarizer", [r"\bsummar(y|ize)|tl;dr\b"]),
]

def _route_for(task: str) -> tuple[str, str]:
    lower = task.lower()
    for agent, patterns in ROUTES:
        for pat in patterns:
            if re.search(pat, lower):
                return agent, f"Matched pattern '{pat}' for agent '{agent}'"
    return "summarizer", "Default route to 'summarizer'"

@tool(
    "agent_router",
    "Suggest the best named agent for a task from the local catalog.",
    parameters={"type": "object", "properties": {"task": {"type": "string"}}, "required": ["task"]},
)
async def agent_router(task: str) -> dict:
    agent, reason = _route_for(task)
    return {"agent": agent, "reason": reason, "available": list(CATALOG.keys())}

@tool(
    "route_and_delegate",
    "Route a task to the best agent and immediately delegate the work.",
    parameters={
        "type": "object",
        "properties": {
            "task": {"type": "string"},
            "provider": {"type": "string"}
        },
        "required": ["task"]
    },
)
async def route_and_delegate(task: str, provider: str | None = None) -> dict:
    agent, _ = _route_for(task)
    return await delegate_agent(
        prompt=f"{CATALOG.get(agent, '')}\n\nTask:\n{task}",
        provider=provider
    )

