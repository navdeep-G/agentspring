import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000/v1"
API_KEY = "test-api-key"

async def list_tools():
    """List all available tools."""
    headers = {
        "X-API-Key": API_KEY,
        "Accept": "application/json"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/tools",
            headers=headers
        )
        response.raise_for_status()
        return response.json()

async def run_agent(prompt: str, input_text: str):
    """Run an agent with the given prompt and input."""
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    payload = {
        "prompt": prompt,
        "input": input_text
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/agents/run",
            json=payload,
            headers=headers,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()

async def main():
    try:
        print("1. Checking available tools...")
        tools = await list_tools()
        print(f"Available tools: {json.dumps(tools, indent=2)}")
        
        print("\n2. Running agent with simple prompt...")
        response = await run_agent(
            prompt="You are a helpful assistant.",
            input_text="Hello, how are you?"
        )
        print(f"Agent response: {json.dumps(response, indent=2)}")

    except httpx.HTTPStatusError as e:
        print(f"\nHTTP error ({e.response.status_code}): {e.response.text}")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
    finally:
        print("\nScript completed.")

if __name__ == "__main__":
    asyncio.run(main())