from .celery_app import celery_app
from .ingestion import s3_iter_objects, gcs_iter_objects, extract_text, chunk_text, _hash
from .tools.builtin_rag import rag_upsert
@celery_app.task(autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def ingest_s3_task(tenant_id: str, collection: str, bucket: str, prefix: str = "", chunk_size: int = 1200, chunk_overlap: int = 200):
    items = s3_iter_objects(bucket, prefix); count=0
    import asyncio
    async def _run():
        nonlocal count
        for key, data in items:
            text = extract_text(key, data)
            for idx, ch in enumerate(chunk_text(text, chunk_size, chunk_overlap), 1):
                did = f"s3:{bucket}/{key}#{_hash(data)}#part{idx}"
                await rag_upsert(tenant_id=tenant_id, collection=collection, doc_id=did, text=ch, metadata={"source":"s3","bucket":bucket,"key":key})
                count+=1
    asyncio.run(_run()); return {"ok": True, "chunks": count}
@celery_app.task(autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def ingest_gcs_task(tenant_id: str, collection: str, bucket: str, prefix: str = "", chunk_size: int = 1200, chunk_overlap: int = 200):
    items = gcs_iter_objects(bucket, prefix); count=0
    import asyncio
    async def _run():
        nonlocal count
        for key, data in items:
            text = extract_text(key, data)
            for idx, ch in enumerate(chunk_text(text, chunk_size, chunk_overlap), 1):
                did = f"gcs:{bucket}/{key}#{_hash(data)}#part{idx}"
                await rag_upsert(tenant_id=tenant_id, collection=collection, doc_id=did, text=ch, metadata={"source":"gcs","bucket":bucket,"key":key})
                count+=1
    asyncio.run(_run()); return {"ok": True, "chunks": count}
