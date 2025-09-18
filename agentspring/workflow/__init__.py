from typing import Any, Dict, AsyncGenerator
from agentspring.tools import tool_registry
from agentspring.planner import Plan
class Workflow:
    def __init__(self, plan: Plan, default_input: str):
        self.plan=plan; self.default_input=default_input; self.outputs: Dict[str, Any] = {}
    async def execute(self) -> Dict[str, Any]:
        async for _ in self.execute_stream(): pass
        return self.outputs
    async def execute_stream(self) -> AsyncGenerator[Dict[str, Any], None]:
        done=set(); nodes={n.id:n for n in self.plan.nodes}
        while len(done)<len(nodes):
            progressed=False
            for nid,node in nodes.items():
                if nid in done: continue
                if all(dep in done for dep in node.depends_on):
                    yield {"type":"node_start","node_id":nid,"tool":node.tool}
                    try:
                        res=await tool_registry.invoke(node.tool, node.args)
                        self.outputs[nid]=res; yield {"type":"node_output","node_id":nid,"output":res}
                        done.add(nid); progressed=True
                    except Exception as e:
                        yield {"type":"node_error","node_id":nid,"error":str(e)}; done.add(nid); progressed=True
            if not progressed: yield {"type":"error","message":"Deadlock in plan execution"}; break
        yield {"type":"done","outputs":self.outputs}
