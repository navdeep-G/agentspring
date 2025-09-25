import json
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from agentspring.tools import ToolRegistry, tool_registry
from agentspring.llm import get_provider

class PlanNode(BaseModel):
    id: str
    type: str = "tool"
    tool: str
    args: Dict[str, Any] = Field(default_factory=dict)
    depends_on: List[str] = Field(default_factory=list)

class Plan(BaseModel):
    workflow_id: str
    name: str
    nodes: List[PlanNode]

PROMPT_TEMPLATE = """You are a planner for an AI agent system.
Given a user request, produce a minimal JSON plan to solve it using available tools.
Use these tools (name: description):
{tool_docs}
Return ONLY JSON with fields: workflow_id, name, nodes[]. Each node: id, type='tool', tool, args, depends_on."""

class Planner:
    def __init__(self, tools: ToolRegistry, provider_name: str = "mock"):
        self.tools = tools
        self.provider = get_provider(provider_name)

    async def plan_async(self, user_request: str, default_input: str, workflow_id: str, name: str) -> Plan:
        tool_docs = "\n".join([f"- {t['function']['name']}: {t['function']['description']}" for t in self.tools.to_openai_functions()])
        system="You output only valid JSON for the plan schema."
        prompt = PROMPT_TEMPLATE.format(tool_docs=tool_docs) + "\nUser request: " + user_request
        out = await self.provider.generate_async(prompt, messages=[{"role":"system","content":system},{"role":"user","content":prompt}], response_json=True)
        plan_data = json.loads(out) if isinstance(out, str) else out
        valid = {t['function']['name'] for t in self.tools.to_openai_functions()}
        nodes=[PlanNode(**n) for n in plan_data.get("nodes", []) if n.get("tool") in valid] or [PlanNode(id="n1", tool="math_eval", args={"expr":"1+1"})]
        return Plan(workflow_id=workflow_id, name=name, nodes=nodes)

    def build_workflow(self, plan: Plan, default_input: str, workflow_id: str, name: str):
        from agentspring.workflow import Workflow
        return Workflow(plan, default_input)
