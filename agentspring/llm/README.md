# LLM Provider System

A flexible and extensible system for integrating multiple LLM providers with support for sync/async operations, rate limiting, and error handling.

## Features

- **Provider Registry**: Register and manage multiple LLM providers
- **Async/Sync Support**: Native support for both synchronous and asynchronous operations
- **Rate Limiting**: Built-in rate limiting with configurable limits
- **Error Handling**: Comprehensive error handling with retries
- **Input Validation**: Automatic input validation
- **Logging**: Detailed logging for debugging and monitoring

## Available Providers

- **Ollama**: Default provider for local Ollama models

## Usage

### Basic Usage

```python
from agentspring.llm import LLMHelper

# Create a helper with default provider (Ollama)
llm = LLMHelper()

# Generate text
response = llm.generate("Hello, world!")
print(response)

# Stream text
for chunk in llm.stream("Stream this text"):
    print(chunk, end="", flush=True)
```

### Async Usage

```python
import asyncio
from agentspring.llm import LLMHelper

async def main():
    llm = LLMHelper()
    
    # Async generation
    response = await llm.generate_async("Hello, async world!")
    print(response)
    
    # Async streaming
    async for chunk in llm.stream_async("Stream this asynchronously"):
        print(chunk, end="", flush=True)

asyncio.run(main())
```

### Custom Configuration

```python
from agentspring.llm import LLMHelper

# Custom configuration
llm = LLMHelper(
    provider="ollama",  # or any registered provider
    model="llama3.2",
    base_url="http://localhost:11434",
    config={
        "timeout": 30,  # seconds
        "max_retries": 3,
        "rate_limit": {
            "requests_per_minute": 60,
            "max_concurrent": 10,
            "retry_after": 60  # seconds
        },
        "validate_input": True
    }
)
```

## Creating a Custom Provider

1. Create a new provider class that inherits from `LLMProvider`:

```python
from agentspring.llm import LLMProvider, LLMRegistry

@LLMRegistry.register("my_provider")
class MyLLMProvider(LLMProvider):
    def __init__(self, **kwargs):
        super().__init__(kwargs.get('config'))
        # Initialize your provider here
        self.model = kwargs.get('model', 'default-model')
    
    async def generate_async(self, prompt: str, **kwargs) -> str:
        # Implement async text generation
        return "Generated text"
    
    async def stream_async(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        # Implement async text streaming
        yield "Streamed "
        yield "text"
```

2. Use your custom provider:

```python
from agentspring.llm import LLMHelper

llm = LLMHelper(
    provider="my_provider",
    model="custom-model",
    # Other provider-specific parameters
)
```

## Error Handling

The system provides several built-in exceptions:

- `LLMError`: Base exception for all LLM-related errors
- `RateLimitError`: Raised when rate limits are exceeded
- `OllamaAPIError`: Provider-specific errors for Ollama

Example error handling:

```python
from agentspring.llm import LLMHelper, RateLimitError

try:
    llm = LLMHelper()
    response = llm.generate("Test prompt")
except RateLimitError as e:
    print(f"Rate limited. Try again in {e.retry_after} seconds")
except Exception as e:
    print(f"Error: {str(e)}")
```

## Logging

Logging is automatically configured with the following format:

```
[timestamp] [level] [provider] message
```

To configure logging:

```python
import logging

# Set log level
logging.basicConfig(level=logging.INFO)

# Get logger for a specific provider
logger = logging.getLogger("llm.provider.ollama")
```

## Testing

Run the test suite:

```bash
pytest tests/test_llm_providers.py -v
```

## Dependencies

- Python 3.8+
- aiohttp
- tenacity
- pydantic
- pytest (for testing)

## License

MIT
