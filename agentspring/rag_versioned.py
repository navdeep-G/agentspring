import uuid
from sqlalchemy import select, text as sqltext
from .db.session import SessionLocal
from .db.models_versioned import Collection, RagChunk
from .config import settings
from openai import AsyncOpenAI
import os

def _get_client() -> AsyncOpenAI:
    key = settings.OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY must be set for versioned RAG.")
    return AsyncOpenAI(api_key=key)

async def ensure_collection(tenant_id: str, slug: str, name: str | None = None) -> dict:
    async with SessionLocal() as s:
        res = await s.execute(select(Collection).where(Collection.tenant_id == uuid.UUID(tenant_id), Collection.slug == slug))
        c = res.scalar_one_or_none()
        if c:
            return {"id": str(c.id), "slug": c.slug, "name": c.name, "latest_version": c.latest_version}
        c = Collection(tenant_id=uuid.UUID(tenant_id), slug=slug, name=name or slug)
        s.add(c); await s.commit(); await s.refresh(c)
        return {"id": str(c.id), "slug": c.slug, "name": c.name, "latest_version": c.latest_version}

async def bump_version(tenant_id: str, slug: str) -> dict:
    async with SessionLocal() as s:
        res = await s.execute(select(Collection).where(Collection.tenant_id == uuid.UUID(tenant_id), Collection.slug == slug))
        c = res.scalar_one_or_none()
        if not c: raise ValueError("collection not found")
        c.latest_version += 1
        await s.commit(); await s.refresh(c)
        return {"id": str(c.id), "slug": c.slug, "latest_version": c.latest_version}

async def upsert_chunk(collection_id: str, version: int, doc_id: str, text: str, metadata: dict | None = None):
    client = _get_client()
    emb = (await client.embeddings.create(model=settings.EMBEDDING_MODEL, input=text)).data[0].embedding
    async with SessionLocal() as s:
        await s.execute(
            sqltext(
                """
                INSERT INTO rag_chunks (id, collection_id, version, doc_id, embedding, content, metadata, created_at)
                VALUES (gen_random_uuid(), :cid, :ver, :doc, :emb, :txt, :meta, NOW())
                ON CONFLICT (collection_id, version, doc_id)
                DO UPDATE SET embedding=:emb, content=:txt, metadata=:meta
                """
            ),
            {"cid": uuid.UUID(collection_id), "ver": version, "doc": doc_id, "emb": emb, "txt": text, "meta": metadata or {}},
        )
        await s.commit()
    return "ok"

async def retrieve_chunks(collection_id: str, version: int, query: str, k: int = 5) -> list:
    client = _get_client()
    qemb = (await client.embeddings.create(model=settings.EMBEDDING_MODEL, input=query)).data[0].embedding
    async with SessionLocal() as s:
        rows = (
            await s.execute(
                sqltext(
                    """
                    SELECT id, doc_id, content, metadata, 1 - (embedding <=> :vec) AS score
                    FROM rag_chunks
                    WHERE collection_id = :cid AND version = :ver
                    ORDER BY embedding <=> :vec
                    LIMIT :k
                    """
                ),
                {"vec": qemb, "cid": uuid.UUID(collection_id), "ver": version, "k": k},
            )
        ).mappings().all()
        return [dict(r) for r in rows]
