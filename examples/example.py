"""
AgentSpring Core Features Example
-------------------------------
This example showcases the core features of AgentSpring:
1. Tool registration and usage
2. LLM provider integration
3. Simple interaction with LLM and tools
"""

import asyncio
import json

import aiohttp

from agentspring.llm import LLMProvider, register_provider
from agentspring.tools import tool, tool_registry


# 1. Define a custom LLM provider for Ollama
class OllamaProvider(LLMProvider):
    def __init__(
        self,
        model: str = "llama3.2:latest",
        base_url: str = "http://localhost:11434",
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.session = None

    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def generate_async(self, prompt: str, **kwargs) -> str:
        """Generate a response using Ollama's API."""
        session = await self._get_session()
        try:
            async with session.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=aiohttp.ClientTimeout(total=60),
            ) as response:
                response.raise_for_status()
                result = await response.json()
                return result.get("response", "")
        except Exception as e:
            return f"Error generating response: {str(e)}"

    async def stream_async(self, prompt: str, **kwargs) -> str:
        """Stream a response using Ollama's API."""
        session = await self._get_session()
        try:
            async with session.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": True},
                timeout=aiohttp.ClientTimeout(total=60),
            ) as response:
                response.raise_for_status()
                async for line in response.content:
                    if line:
                        try:
                            chunk = json.loads(line)
                            if "response" in chunk:
                                yield chunk["response"]
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            yield f"Error streaming response: {str(e)}"

    async def close(self):
        """Clean up resources."""
        if self.session and not self.session.closed:
            await self.session.close()


# Register the provider
register_provider("ollama")(OllamaProvider)


# 2. Define some tools
@tool("word_count", "Count the number of words in a given text")
async def word_count(text: str) -> str:
    count = len(text.split())
    return f"The text contains {count} words."


@tool("to_uppercase", "Convert a given text to uppercase")
async def to_uppercase(text: str) -> str:
    return text.upper()


# 3. Main function
async def check_ollama_connection() -> bool:
    """Check if Ollama is running and accessible."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "http://localhost:11434/api/tags", timeout=2
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("\n📡 Ollama is running!")
                    print(
                        f"Available models: {[m['name'] for m in data.get('models', [])]}"
                    )
                    return True
                return False
    except Exception as e:
        print(f"🔴 Could not connect to Ollama: {str(e)}")
        return False


async def main():
    # Check if Ollama is running
    print("🔍 Checking Ollama connection...")
    if not await check_ollama_connection():
        print("\n❌ Ollama is not running. Please start it with:")
        print("   $ ollama serve")
        return

    # Initialize LLM
    llm = OllamaProvider()

    # Register the provider
    register_provider("ollama")(OllamaProvider)

    # Register tools
    tool_registry.register(
        "word_count", "Count the number of words in a given text"
    )(word_count)
    tool_registry.register(
        "to_uppercase", "Convert a given text to uppercase"
    )(to_uppercase)

    print("AgentSpring Example - Type 'exit' to quit")
    print("Available tools:")
    for tool_name, tool_info in tool_registry.get_all_schemas().items():
        print(f"- {tool_name}: {tool_info.description}")

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("Goodbye!")
                break

            # Use the LLM for general responses
            response = await llm.generate_async(user_input)
            print(f"Agent: {response}")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    # Cleanup
    await llm.close()


if __name__ == "__main__":
    asyncio.run(main())
