import json, asyncio
from ..base import LLMProvider
from ..registry import register_provider

@register_provider("mock")
class MockProvider(LLMProvider):
    async def generate_async(self, prompt: str, **kwargs) -> str:
        # Return a tiny plan that runs the built-in math tool (no network, no keys)
        if kwargs.get("response_json"):
            plan = {
                "workflow_id": "mock",
                "name": "mock-plan",
                "nodes": [
                    {"id": "n1", "type": "tool", "tool": "math_eval",
                     "args": {"expr": "2+2"}, "depends_on": []}
                ],
            }
            return json.dumps(plan)
        return f"MOCK: {prompt}"

    async def stream_async(self, prompt: str, **kwargs):
        for ch in "mock-stream":
            yield ch
            await asyncio.sleep(0)
