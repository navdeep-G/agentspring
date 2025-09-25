import httpx
import asyncio
import json

async def discover_endpoints(base_url: str, api_key: str):
    """Discover available API endpoints."""
    endpoints = [
        "/",
        "/tools",
        "/agents",
        "/agents/run",
        "/v1",
        "/v1/tools",
        "/v1/agents/run",
        "/admin",
        "/admin/providers",
        "/api",
        "/api/v1",
        "/docs",
        "/openapi.json"
    ]
    
    headers = {
        "X-API-Key": api_key,
        "Accept": "application/json"
    }
    
    print(f"Testing endpoints at base URL: {base_url}")
    print("-" * 50)
    
    for endpoint in endpoints:
        url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=5.0)
                print(f"{url} - {response.status_code} {response.reason_phrase}")
                if response.status_code < 400:
                    try:
                        print(f"Response: {json.dumps(response.json(), indent=2)[:200]}...")
                    except:
                        print("Response: [Non-JSON response]")
        except Exception as e:
            print(f"{url} - Error: {str(e)}")
        print("-" * 50)

async def main():
    base_url = "http://localhost:8000"
    api_key = "test-api-key"
    
    print("Starting endpoint discovery...\n")
    await discover_endpoints(base_url, api_key)

if __name__ == "__main__":
    asyncio.run(main())