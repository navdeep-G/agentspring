"""
Planner: turns natural-language goals into a Workflow.
- Uses ToolRegistry schemas to constrain tool choices/params
- Uses an LLM provider (if available) to propose a JSON plan
- Falls back to a simple keyword heuristic if no LLM is configured
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from pydantic import BaseModel, Field

from ..tools import tool_registry, ToolRegistry
from ..workflow import Workflow, NodeType

if TYPE_CHECKING:
    # For type-checkers only; not executed at runtime
    from ..llm import LLMProvider


DEFAULT_PROMPT = """You are a senior workflow planner. Given a user instruction
and the available tools (with names and parameter schemas), output a JSON object with this schema:

{
  "steps": [
    {
      "id": "step-1",
      "tool_name": "<one of the allowed tool names>",
      "parameters": { ... },
      "reasoning": "why this step",
      "depends_on": ["<optional previous step ids>"]
    }
  ]
}

Rules:
- Only use tool names from the provided list.
- If a parameter is not needed, omit it.
- Prefer 1-5 concise steps.
- Do NOT include any text outside the JSON object.
Tools:
{tools}
User instruction: {prompt}
"""

def _extract_main_text(s: str) -> str:
    """
    If the user provided a quoted block, prefer that as the text payload.
    Supports triple or single/double quotes. Falls back to the original.
    """
    # triple-quoted block
    m = re.search(r'"""([\s\S]*?)"""', s)
    if m and m.group(1).strip():
        return m.group(1).strip()

    # longest single/double-quoted block
    blocks = re.findall(r'"([^"]+)"|\'([^\']+)\'', s)
    merged = [b[0] or b[1] for b in blocks]
    if merged:
        # pick the longest quoted span
        return max(merged, key=len).strip()

    return s.strip()

class PlanStep(BaseModel):
    id: str
    tool_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    reasoning: Optional[str] = None
    depends_on: List[str] = Field(default_factory=list)


class Plan(BaseModel):
    steps: List[PlanStep] = Field(default_factory=list)


class Planner:
    def __init__(
        self,
        llm: Optional["LLMProvider"] = None,
        tools: Optional[ToolRegistry] = None,
        prompt_template: str = DEFAULT_PROMPT,
    ) -> None:
        self.tools = tools or tool_registry
        self.llm = llm if llm is not None else self._try_get_default_llm()
        self.prompt_template = prompt_template

    def _try_get_default_llm(self) -> Optional["LLMProvider"]:
        """Lazy-import the default LLM provider to avoid import-time failures."""
        try:
            from ..llm import get_provider  # type: ignore
            return get_provider()
        except Exception:
            return None

    def _tools_markdown(self) -> str:
        schemas = self.tools.get_all_schemas()
        lines: List[str] = []
        for name, schema in schemas.items():
            desc = (schema.description or "").strip()
            params = schema.parameters or {}
            lines.append(f"- {name}: {desc}")
            if params:
                lines.append("  params:" + json.dumps(params))
        return "\n".join(lines)

    def _prompt(self, user_prompt: str) -> str:
        # Avoid str.format() so literal JSON braces don't break the template
        return (
            self.prompt_template
            .replace("{tools}", self._tools_markdown())
            .replace("{prompt}", user_prompt)
        )

    def _extract_json(self, text: str) -> str:
        # Prefer fenced code block
        m = re.search(r"```(?:json\n)?([\s\S]*?)\n```", text)
        if m:
            return m.group(1).strip()
        # Fallback to first {...} blob
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            return m.group(0)
        raise ValueError("No JSON object found in LLM output")

    async def plan(self, user_prompt: str) -> Plan:
        # If no LLM, return a trivial heuristic plan
        if self.llm is None:
            return self._heuristic_plan(user_prompt)

        raw = await self.llm.generate_async(self._prompt(user_prompt))
        try:
            data = json.loads(self._extract_json(raw))
            return Plan(**data)
        except Exception as e:
            # Fallback to heuristic if parsing fails
            return self._heuristic_plan(user_prompt, error=str(e))

    def _heuristic_plan(self, user_prompt: str, error: Optional[str] = None) -> Plan:
        # Very simple heuristic: pick the first available tool and pass the user text
        schemas = self.tools.get_all_schemas()
        tool_name = next(iter(schemas.keys()), None)
        if tool_name is None:
            return Plan(steps=[])
        return Plan(
            steps=[
                PlanStep(
                    id="step-1",
                    tool_name=tool_name,
                    parameters={"text": user_prompt},
                    reasoning=(
                        "heuristic fallback"
                        if error is None
                        else f"heuristic due to {error}"
                    ),
                    depends_on=[],
                )
            ]
        )

    def build_workflow(
        self,
        plan: Plan,
        workflow_id: str = "wf-1",
        name: str = "Planned Workflow",
        default_input: Optional[str] = None,
    ) -> Workflow:
        """
        Build a Workflow from a Plan, with safety:
        - skip unknown tools
        - normalize duplicate/empty step ids
        - drop deps to unknown steps
        - auto-fill a missing text-like parameter from `default_input`
        """
        wf = Workflow(workflow_id=workflow_id, name=name)
        wf.tools = self.tools

        # at the start of build_workflow(), after wf.tools = self.tools
        text_param_names = ("text", "input", "prompt", "content")
        schemas = self.tools.get_all_schemas()
        main_text = _extract_main_text(default_input or "") if default_input else None


        # Keep only steps with known tools
        kept: List[PlanStep] = [s for s in plan.steps if self.tools.get_tool(s.tool_name)]
        if not kept:
            fallback = self._heuristic_plan("No valid steps/tools in plan")
            kept = fallback.steps

        # Normalize IDs
        used_ids: set[str] = set()
        normalized: List[PlanStep] = []
        next_i = 1
        for step in kept:
            sid = (getattr(step, "id", "") or "").strip()
            if not sid or sid in used_ids:
                while True:
                    sid = f"step-{next_i}"
                    next_i += 1
                    if sid not in used_ids:
                        break
            used_ids.add(sid)
            normalized.append(
                PlanStep(
                    id=sid,
                    tool_name=step.tool_name,
                    parameters=step.parameters or {},
                    reasoning=step.reasoning,
                    depends_on=list(step.depends_on or []),
                )
            )

        valid_ids = used_ids
        for step in normalized:
            step.depends_on = [d for d in (step.depends_on or []) if d in valid_ids]

        # Autocomplete typical text params when missing
        schemas = self.tools.get_all_schemas()
        text_param_names = ("text", "input", "prompt", "content")

        for step in normalized:
            params = dict(step.parameters or {})
            schema = schemas.get(step.tool_name)
            if schema and isinstance(schema.parameters, dict):
                needs_text = any(name in schema.parameters for name in text_param_names)
                missing_text = all(name not in params for name in text_param_names)
                if needs_text and missing_text and main_text:
                    target_name = next(
                        (n for n in ("text", "input", "prompt", "content") if n in schema.parameters),
                        "text",
                    )
                    params[target_name] = main_text
            step.parameters = params


        # Add nodes
        for step in normalized:
            wf.add_node(
                node_id=step.id,
                node_type=NodeType.TOOL,
                config={"tool_name": step.tool_name, "parameters": step.parameters},
                dependencies=step.depends_on,
            )

        return wf

    async def plan_workflow(self, user_prompt: str, workflow_id: str = "wf-1") -> Workflow:
        plan = await self.plan(user_prompt)
        return self.build_workflow(
            plan,
            workflow_id=workflow_id,
            name=f"Plan for: {user_prompt[:50]}",
            default_input=user_prompt,          # <-- pass original instruction for autofill
        )



__all__ = ["Planner", "Plan", "PlanStep"]
