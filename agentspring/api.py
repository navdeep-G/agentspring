import json, uuid
from fastapi import FastAPI, Depends, Header, HTTPException, Query, UploadFile, File, Form, Body
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from .metrics import setup_metrics
from .observability import setup_logging, setup_tracing, setup_sentry
from .rate_limit import setup_rate_limiter
from .config import settings
from .llm.providers import mock as _reg0  # noqa  (registers the mock provider)
from .llm.providers import openai as _reg1  # noqa
from .llm.providers import azure_openai as _reg2  # noqa
from .llm.providers import anthropic as _reg3  # noqa
from .tools import builtin_http, builtin_math, builtin_embeddings, builtin_rag  # noqa
from .planner import Planner
from .workflow import Workflow
from .multi_tenancy import get_tenant_by_api_key, create_tenant, create_tenant_user, list_tenant_users, delete_tenant_user
from fastapi_limiter.depends import RateLimiter
from .db.session import SessionLocal
from .db import models_versioned as _mv  # ensure tables registered
from .db.models import Run
from .auth_oidc import verify_bearer, OIDCError
from .ingestion import extract_text, chunk_text
from .tasks_ingest import ingest_s3_task, ingest_gcs_task
from .rag_versioned import ensure_collection, bump_version, upsert_chunk, retrieve_chunks
from .uploads_sign import s3_sign_post, gcs_sign_put
# near other imports in api.py
from .tools import delegate, agents_catalog, router, critic, consensus  # noqa: F401

app = FastAPI(title="AgentSpring — Final Bundle")
setup_metrics(app)

from agentspring.middleware.agent_depth import AgentDepthMiddleware
app.add_middleware(AgentDepthMiddleware)

from fastapi import HTTPException, Body
from fastapi.responses import JSONResponse
from .tools import registry as tool_registry

@app.get("/v1/tools")
async def list_tools():
    return sorted(tool_registry.keys())

# at top with other imports
import inspect
from anyio import to_thread
from fastapi import HTTPException, Body, Request
from fastapi.responses import JSONResponse
from .tools import registry as tool_registry
from inspect import Parameter

@app.post("/v1/tools/{name}")
async def call_tool(
    name: str,
    request: Request,
    payload: dict = Body(...),
):
    fn = tool_registry.get(name)
    if not fn:
        raise HTTPException(status_code=404, detail=f"Unknown tool '{name}'")

    caller_headers = {"X-API-Key": request.headers.get("x-api-key")}

    # Build kwargs only with params the tool supports
    params = inspect.signature(fn).parameters
    accepts_var_kw = any(p.kind == Parameter.VAR_KEYWORD for p in params.values())

    call_kwargs = dict(payload or {})
    if "__caller_headers__" in params or accepts_var_kw:
        call_kwargs["__caller_headers__"] = caller_headers

    try:
        if inspect.iscoroutinefunction(fn):
            result = await fn(**call_kwargs)               # async tool
        else:
            result = await to_thread.run_sync(             # sync tool
                lambda: fn(**call_kwargs)
            )
    except TypeError as e:
        raise HTTPException(status_code=400, detail=f"Bad args for '{name}': {e}")
    except Exception as e:
        # Let FastAPI show a 500 with the message
        raise

    return JSONResponse({"tool": name, "output": result}, status_code=200)

# CORS for console
if settings.CORS_ALLOWED_ORIGINS:
    origins = [o.strip() for o in settings.CORS_ALLOWED_ORIGINS.split(",") if o.strip()]
    app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def on_startup():
    setup_logging(); setup_sentry(); setup_tracing("agentspring"); await setup_rate_limiter(app)

def oidc_required(authorization: Optional[str] = Header(None, alias="Authorization")):
    if settings.REQUIRE_OIDC:
        if not authorization or not authorization.lower().startswith("bearer "):
            raise HTTPException(401, "Bearer token required")
        token = authorization.split(" ",1)[1]
        try: claims = verify_bearer(token)
        except OIDCError as e: raise HTTPException(401, f"Invalid token: {e}")
        return claims
    return None

def tenant_dep(x_api_key: Optional[str] = Header(None, alias="X-API-Key"), claims=Depends(oidc_required)) -> dict:
    if settings.API_KEY:
        if x_api_key != settings.API_KEY: raise HTTPException(401, "Invalid API key")
        return {"id":"dev-tenant","name":"dev","role":"admin"}
    if not x_api_key: raise HTTPException(401, "Missing X-API-Key")
    return {"api_key": x_api_key}

async def resolve_tenant(tenant_hint: dict):
    if "id" in tenant_hint: return tenant_hint
    t = await get_tenant_by_api_key(tenant_hint["api_key"])
    if not t: raise HTTPException(401, "Invalid API key")
    return {"id": t["id"], "name": t["name"], "role": t.get("role","viewer")}

def require_admin(x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")):
    if not settings.ADMIN_API_KEY or x_admin_key != settings.ADMIN_API_KEY: raise HTTPException(403, "Admin key required")
    return True

@app.get("/health")
async def health():
    return {"ok": True}

@app.get("/v1/providers")
async def list_providers():
    return ["openai", "azure_openai", "anthropic"]
@app.get("/v1/tools", dependencies=[Depends(RateLimiter(times=20, seconds=60))])
async def list_tools(tenant=Depends(tenant_dep)):
    fns=tool_registry.to_openai_functions(); return [{"name":f["function"]["name"],"description":f["function"]["description"]} for f in fns]

@app.post("/v1/agents/run", dependencies=[Depends(RateLimiter(times=1, seconds=1))])
async def run_agent(body: dict, tenant_hint=Depends(tenant_dep)):
    tenant=await resolve_tenant(tenant_hint); prompt = body.get("prompt") or ""; provider = body.get("provider") or settings.DEFAULT_PROVIDER; stream=bool(body.get("stream"))
    planner=Planner(tools=tool_registry, provider_name=provider); plan=await planner.plan_async(prompt,prompt,str(uuid.uuid4()),"ad-hoc")
    wf:Workflow=planner.build_workflow(plan, default_input=prompt, workflow_id=plan.workflow_id, name=plan.name)
    async with SessionLocal() as s:
        run=Run(tenant_id=uuid.UUID(tenant["id"]), input=prompt, status="running"); s.add(run); await s.commit(); await s.refresh(run); run_id=str(run.id)
    async def gen():
        try:
            async for event in wf.execute_stream():
                yield f"data: {json.dumps(event)}\n\n"
        finally:
            async with SessionLocal() as s2:
                r = await s2.get(Run, uuid.UUID(run_id))
                if r: r.output=wf.outputs; r.status="done"; await s2.commit()
            yield f"data: {json.dumps({'type':'done','run_id': run_id})}\n\n"
    if stream: return StreamingResponse(gen(), media_type="text/event-stream")
    else:
        async for _ in wf.execute_stream(): pass
        return {"run_id": run_id, "result": wf.outputs, "plan": plan.model_dump()}

@app.get("/v1/runs")
async def list_runs(limit: int = 20, offset: int = 0, tenant_hint=Depends(tenant_dep)):
    tenant=await resolve_tenant(tenant_hint)
    async with SessionLocal() as s:
        rows = await s.execute("""SELECT id, status, created_at FROM runs WHERE tenant_id = :tid ORDER BY created_at DESC LIMIT :lim OFFSET :off""", {"tid": uuid.UUID(tenant["id"]), "lim": limit, "off": offset})
        items = [dict(id=str(r[0]), status=r[1], created_at=r[2].isoformat()) for r in rows]
    return {"items": items, "limit": limit, "offset": offset}

@app.get("/v1/runs/{run_id}")
async def get_run(run_id: str, tenant_hint=Depends(tenant_dep)):
    tenant=await resolve_tenant(tenant_hint)
    async with SessionLocal() as s:
        r = await s.get(Run, uuid.UUID(run_id))
        if not r: raise HTTPException(404,"not found")
        if str(r.tenant_id) != tenant["id"]: raise HTTPException(403,"forbidden")
        return {"id": run_id, "status": r.status, "output": r.output, "created_at": r.created_at.isoformat()}

# RAG endpoints
@app.post("/v1/collections/{collection}/docs")
async def upsert_doc(collection: str, body: dict, tenant_hint=Depends(tenant_dep)):
    tenant=await resolve_tenant(tenant_hint)
    from .tools.builtin_rag import rag_upsert
    doc_id=body.get("doc_id"); text=body.get("text"); metadata=body.get("metadata") or {}
    if not doc_id or not text: raise HTTPException(400,"doc_id and text required")
    await rag_upsert(tenant_id=tenant["id"], collection=collection, doc_id=doc_id, text=text, metadata=metadata)
    return {"ok": True}

@app.get("/v1/collections/{collection}/search")
async def search_collection(collection: str, q: str = Query(...), k: int = Query(5), tenant_hint=Depends(tenant_dep)):
    tenant=await resolve_tenant(tenant_hint); from .tools.builtin_rag import rag_retrieve
    res=await rag_retrieve(tenant_id=tenant["id"], collection=collection, query=q, k=k); return {"results": res}

@app.post("/v1/collections/{collection}/ingest")
async def ingest_file(collection: str, tenant_hint=Depends(tenant_dep), file: UploadFile = File(...), doc_id: Optional[str] = Form(None), chunk_size: int = Form(1200), chunk_overlap: int = Form(200)):
    tenant=await resolve_tenant(tenant_hint); content = await file.read()
    text = extract_text(file.filename, content); idx=0
    from .tools.builtin_rag import rag_upsert
    for idx, ch in enumerate(chunk_text(text, chunk_size, chunk_overlap), 1):
        did = doc_id or file.filename or "upload"
        await rag_upsert(tenant_id=tenant["id"], collection=collection, doc_id=f"{did}#part{idx}", text=ch, metadata={"source":"upload","file":file.filename})
    return {"ok": True, "chunks": idx}

# Cloud ingestion triggers (editor/admin roles)
@app.post("/v1/collections/{collection}/ingest/s3")
async def trigger_ingest_s3(collection: str, body: dict, tenant_hint=Depends(tenant_dep)):
    tenant=await resolve_tenant(tenant_hint)
    if tenant.get("role") not in ("admin","editor"): raise HTTPException(403, "editor or admin required")
    bucket = body.get("bucket"); prefix = body.get("prefix",""); size=int(body.get("chunk_size",1200)); ov=int(body.get("chunk_overlap",200))
    if not bucket: raise HTTPException(400, "bucket required")
    res = ingest_s3_task.delay(tenant["id"], collection, bucket, prefix, size, ov); return {"queued": True, "task_id": res.id}

@app.post("/v1/collections/{collection}/ingest/gcs")
async def trigger_ingest_gcs(collection: str, body: dict, tenant_hint=Depends(tenant_dep)):
    tenant=await resolve_tenant(tenant_hint)
    if tenant.get("role") not in ("admin","editor"): raise HTTPException(403, "editor or admin required")
    bucket = body.get("bucket"); prefix = body.get("prefix",""); size=int(body.get("chunk_size",1200)); ov=int(body.get("chunk_overlap",200))
    if not bucket: raise HTTPException(400, "bucket required")
    res = ingest_gcs_task.delay(tenant["id"], collection, bucket, prefix, size, ov); return {"queued": True, "task_id": res.id}

@app.get("/v1/admin/tenants", dependencies=[Depends(require_admin)])
async def list_tenants():
    from .db.session import SessionLocal
    async with SessionLocal() as s:
        res = await s.execute(
            """SELECT id, name, created_at FROM tenants ORDER BY created_at DESC"""
        )
        return [
            {"id": str(r[0]), "name": r[1], "created_at": r[2].isoformat()}
            for r in res
        ]

@app.post("/v1/admin/tenants", dependencies=[Depends(require_admin)])
async def admin_create_tenant(body: dict):
    name=body.get("name"); api_key=body.get("api_key"); rate_limit=body.get("rate_limit","100/minute")
    if not name or not api_key: raise HTTPException(400,"name and api_key required")
    return await create_tenant(name, api_key, rate_limit)

@app.post("/v1/admin/tenants/{tenant_id}/users", dependencies=[Depends(require_admin)])
async def admin_create_user(tenant_id: str, body: dict):
    name=body.get("name") or "key"; api_key=body.get("api_key"); role=body.get("role","viewer")
    if not api_key: raise HTTPException(400,"api_key required")
    return await create_tenant_user(tenant_id, name, api_key, role)

@app.get("/v1/admin/tenants/{tenant_id}/users", dependencies=[Depends(require_admin)])
async def admin_list_users(tenant_id: str):
    return await list_tenant_users(tenant_id)

@app.delete("/v1/admin/tenants/{tenant_id}/users/{user_id}", dependencies=[Depends(require_admin)])
async def admin_delete_user(tenant_id: str, user_id: str):
    return await delete_tenant_user(tenant_id, user_id)

# -------- Versioned RAG (with roles) --------
@app.post("/v1/collections", tags=["collections"])
async def api_create_collection(body: dict = Body(...), tenant_hint=Depends(tenant_dep)):
    tenant=await resolve_tenant(tenant_hint)
    if tenant.get("role") not in ("admin","editor"): raise HTTPException(403, "editor or admin required")
    slug = body.get("slug") or body.get("name")
    name = body.get("name") or slug
    if not slug: raise HTTPException(400, "slug or name required")
    return await ensure_collection(tenant["id"], slug, name)

@app.post("/v1/collections/{slug}/versions", tags=["collections"])
async def api_bump_version(slug: str, tenant_hint=Depends(tenant_dep)):
    tenant=await resolve_tenant(tenant_hint)
    if tenant.get("role") not in ("admin","editor"): raise HTTPException(403, "editor or admin required")
    return await bump_version(tenant["id"], slug)

@app.post("/v1/collections/{slug}/ingest_v", tags=["collections"])
async def api_ingest_versioned(slug: str, body: dict = Body(...), tenant_hint=Depends(tenant_dep)):
    tenant=await resolve_tenant(tenant_hint)
    if tenant.get("role") not in ("admin","editor"): raise HTTPException(403, "editor or admin required")
    col = await ensure_collection(tenant["id"], slug, slug)
    version = body.get("version", "latest")
    if version == "latest": version = col["latest_version"]
    elif isinstance(version, int): pass
    else: raise HTTPException(400, "version must be int or 'latest'")
    if not body.get("doc_id") or not body.get("text"): raise HTTPException(400, "doc_id and text required")
    await upsert_chunk(col["id"], int(version), body["doc_id"], body["text"], body.get("metadata"))
    return {"ok": True, "collection": slug, "version": int(version)}

@app.get("/v1/collections/{slug}/search_v", tags=["collections"])
async def api_search_versioned(slug: str, q: str, version: str = "latest", k: int = 5, tenant_hint=Depends(tenant_dep)):
    tenant=await resolve_tenant(tenant_hint)
    col = await ensure_collection(tenant["id"], slug, slug)
    ver = col["latest_version"] if version == "latest" else int(version)
    results = await retrieve_chunks(col["id"], ver, q, k)
    return {"results": results, "collection": slug, "version": ver}

# Signed uploads
@app.post("/v1/uploads/s3/sign", tags=["uploads"])
async def api_s3_sign(body: dict = Body(...), tenant_hint=Depends(tenant_dep)):
    tenant=await resolve_tenant(tenant_hint)
    if tenant.get("role") not in ("admin","editor"): raise HTTPException(403, "editor or admin required")
    bucket = body.get("bucket"); key = body.get("key"); expires = int(body.get("expires_seconds", 3600))
    if not bucket or not key: raise HTTPException(400, "bucket and key required")
    return s3_sign_post(bucket, key, expires)

@app.post("/v1/uploads/gcs/sign", tags=["uploads"])
async def api_gcs_sign(body: dict = Body(...), tenant_hint=Depends(tenant_dep)):
    tenant=await resolve_tenant(tenant_hint)
    if tenant.get("role") not in ("admin","editor"): raise HTTPException(403, "editor or admin required")
    bucket = body.get("bucket"); key = body.get("key"); expires = int(body.get("expires_seconds", 3600))
    if not bucket or not key: raise HTTPException(400, "bucket and key required")
    return gcs_sign_put(bucket, key, expires)

from fastapi import HTTPException, Body
from .tools import registry as tool_registry  # wherever your registry lives

@app.get("/v1/tools")
async def list_tools():
    # minimal listing
    return sorted(tool_registry.keys())

@app.post("/v1/tools/{name}")
async def call_tool(name: str, payload: dict = Body(...)):
    tool_fn = tool_registry.get(name)
    if not tool_fn:
        raise HTTPException(status_code=404, detail=f"Unknown tool '{name}'")
    # Tools are async; call with kwargs from payload
    try:
        result = await tool_fn(**payload)
    except TypeError as e:
        raise HTTPException(status_code=400, detail=f"Bad args for '{name}': {e}")
    return {"tool": name, "output": result}

