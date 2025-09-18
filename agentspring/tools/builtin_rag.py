from . import tool
from sqlalchemy import text as sqltext
from agentspring.db.session import SessionLocal
from agentspring.config import settings
from openai import AsyncOpenAI
import os

def _get_client() -> AsyncOpenAI:
    key = settings.OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY must be set to use RAG.")
    return AsyncOpenAI(api_key=key)

@tool(
    "rag_upsert",
    "Upsert a document into a vector collection",
    parameters={
        "type": "object",
        "properties": {
            "tenant_id": {"type": "string"},
            "collection": {"type": "string"},
            "doc_id": {"type": "string"},
            "text": {"type": "string"},
            "metadata": {"type": "object"},
        },
        "required": ["tenant_id", "collection", "doc_id", "text"],
    },
)
async def rag_upsert(tenant_id: str, collection: str, doc_id: str, text: str, metadata: dict = None) -> str:
    client = _get_client()
    emb = (await client.embeddings.create(model=settings.EMBEDDING_MODEL, input=text)).data[0].embedding
    async with SessionLocal() as s:
        await s.execute(
            sqltext(
                """
                INSERT INTO embeddings (id, tenant_id, collection, doc_id, embedding, content, metadata, created_at)
                VALUES (gen_random_uuid(), :tenant_id, :collection, :doc_id, :embedding, :content, :metadata, NOW())
                ON CONFLICT (tenant_id, collection, doc_id)
                DO UPDATE SET embedding=:embedding, content=:content, metadata=:metadata
                """
            ),
            {
                "tenant_id": tenant_id,
                "collection": collection,
                "doc_id": doc_id,
                "embedding": emb,
                "content": text,
                "metadata": metadata or {},
            },
        )
        await s.commit()
    return "ok"

@tool(
    "rag_retrieve",
    "Retrieve top-k docs from a collection using vector similarity",
    parameters={
        "type": "object",
        "properties": {
            "tenant_id": {"type": "string"},
            "collection": {"type": "string"},
            "query": {"type": "string"},
            "k": {"type": "integer", "default": 5},
        },
        "required": ["tenant_id", "collection", "query"],
    },
)
async def rag_retrieve(tenant_id: str, collection: str, query: str, k: int = 5) -> list:
    client = _get_client()
    qemb = (await client.embeddings.create(model=settings.EMBEDDING_MODEL, input=query)).data[0].embedding
    async with SessionLocal() as s:
        rows = (
            await s.execute(
                sqltext(
                    """
                    SELECT id, doc_id, content, metadata, 1 - (embedding <=> :vec) AS score
                    FROM embeddings
                    WHERE tenant_id = :tenant AND collection = :coll
                    ORDER BY embedding <=> :vec
                    LIMIT :k
                    """
                ),
                {"vec": qemb, "tenant": tenant_id, "coll": collection, "k": k},
            )
        ).mappings().all()
        return [dict(r) for r in rows]
