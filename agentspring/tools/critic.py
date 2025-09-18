# agentspring/tools/critic.py
from __future__ import annotations
import re
from . import tool

def _heuristic_score(text: str, require_citations: bool = False) -> tuple[int, list[str]]:
    """Lightweight, deterministic quality scoring with suggestions."""
    suggestions: list[str] = []
    score = 100

    # Basic completeness
    if len(text.strip()) < 40:
        score -= 30
        suggestions.append("Add more detail (content is very short).")

    # Structure
    if text.count("\n") < 1 and len(text) > 200:
        score -= 10
        suggestions.append("Use short paragraphs or bullets for readability.")

    # Hedging / placeholders
    if re.search(r"\b(TBD|???|fixme|lorem)\b", text, re.I):
        score -= 15
        suggestions.append("Remove placeholders (TBD/???/FIXME).")

    # Citations
    if require_citations:
        if not re.search(r"https?://", text):
            score -= 20
            suggestions.append("Add at least one source URL.")

    # Numbers and claims
    if re.search(r"\b(always|never|best)\b", text, re.I):
        suggestions.append("Avoid absolute claims unless justified.")

    score = max(0, min(100, score))
    return score, suggestions

@tool(
    "critic_review",
    "Review text and return a structured verdict with suggestions (no LLM needed).",
    parameters={
        "type": "object",
        "properties": {
            "text": {"type": "string"},
            "require_citations": {"type": "boolean", "default": False}
        },
        "required": ["text"]
    },
)
async def critic_review(text: str, require_citations: bool = False) -> dict:
    score, suggestions = _heuristic_score(text, require_citations)
    verdict = "pass" if score >= 70 else "revise"
    return {"score": score, "verdict": verdict, "suggestions": suggestions}

