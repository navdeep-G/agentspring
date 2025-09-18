from . import tool
from openai import AsyncOpenAI
from agentspring.config import settings
import os

def _get_client() -> AsyncOpenAI:
    key = settings.OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY must be set to use embeddings.")
    return AsyncOpenAI(api_key=key)

@tool(
    "embed_text",
    "Embed text with OpenAI",
    parameters={"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
)
async def embed_text(text: str) -> list:
    client = _get_client()
    resp = await client.embeddings.create(model=settings.EMBEDDING_MODEL, input=text)
    return resp.data[0].embedding
