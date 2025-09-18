# agentspring/tools/consensus.py
from __future__ import annotations
import json
import re
from collections import Counter
from . import tool
from .delegate import fanout_delegate

def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[\.\!\?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]

def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())

def _extract_textish(obj) -> str:
    # Try common fields; fallback to JSON dump
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        for k in ("output", "text", "content", "answer", "final"):
            if k in obj and isinstance(obj[k], str):
                return obj[k]
    try:
        return json.dumps(obj, ensure_ascii=False)
    except Exception:
        return str(obj)

@tool(
    "consensus_merge",
    "Merge multiple short texts into a deduplicated bullet list (deterministic).",
    parameters={"type":"object","properties":{"items":{"type":"array","items":{"type":"string"}}},"required":["items"]},
)
async def consensus_merge(items: list[str]) -> dict:
    sentences = []
    for it in items:
        sentences.extend(_split_sentences(it))
    # Deduplicate by normalized sentence; keep most common first
    norm_map = [_normalize(s) for s in sentences]
    counts = Counter(norm_map)
    unique_ordered = sorted(set(norm_map), key=lambda n: (-counts[n], n))
    # Map back to original casing by first occurrence
    seen = set()
    bullets = []
    for s in sentences:
        n = _normalize(s)
        if n in unique_ordered and n not in seen:
            bullets.append(s if s.endswith(".") else s + ".")
            seen.add(n)
    return {"bullets": bullets[:12], "unique_count": len(bullets)}

@tool(
    "fanout_and_consensus",
    "Run multiple sub-agents in parallel (fanout) and merge their answers into bullets.",
    parameters={
        "type": "object",
        "properties": {
            "prompts": {"type": "array", "items": {"type": "string"}},
            "provider": {"type": "string"}
        },
        "required": ["prompts"]
    },
)
async def fanout_and_consensus(prompts: list[str], provider: str | None = None) -> dict:
    results = await fanout_delegate(prompts=prompts, provider=provider)
    texts = [_extract_textish(r) for r in results]
    merged = await consensus_merge(items=texts)
    return {"results": results, **merged}

