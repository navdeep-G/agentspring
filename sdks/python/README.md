# AgentSpring Python SDK
```python
import asyncio
from agentspring_sdk import AgentSpringClient
async def main():
    client = AgentSpringClient("http://localhost:8000", "acme-key")
    async for ev in client.stream("Summarize https://example.com", provider="openai"):
        print(ev)
    await client.close()
asyncio.run(main())
```
