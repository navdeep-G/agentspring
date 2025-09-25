import json, asyncio
from ..base import LLMProvider
from ..registry import registry

class MockProvider(LLMProvider):
    """A mock LLM provider for testing and development."""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.responses = self.config.get("responses", ["This is a mock response."])
        self.response_index = 0
    
    async def generate_async(self, prompt: str, **kwargs) -> str:
        # Return a tiny plan that runs the built-in math tool (no network, no keys)
        if kwargs.get("response_json"):
            plan = {
                "workflow_id": "mock",
                "name": "mock-plan",
                "nodes": [
                    {
                        "id": "n1",
                        "type": "tool",
                        "tool": "math_eval",
                        "args": {"expr": "1+1"},
                        "depends_on": []
                    }
                ]
            }
            return json.dumps(plan)
        
        # Cycle through responses if multiple provided
        response = self.responses[self.response_index % len(self.responses)]
        self.response_index += 1
        return response
    
    async def stream_async(self, prompt: str, **kwargs):
        response = await self.generate_async(prompt, **kwargs)
        for word in response.split():
            yield word + " "
            await asyncio.sleep(0.05)

# Register the mock provider
registry.register_provider("mock", MockProvider, is_default=True)
