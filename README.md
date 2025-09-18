# AgentSpring

_A lightweight, batteries-included agent runtime for planning and running **tool-driven, multi-agent** workflows over HTTP._

- **API-first:** clean FastAPI endpoints for planning runs and invoking tools.
- **Composable tools:** register Python callables (sync **or** async) with a tiny decorator.
- **Planner-driven:** your chosen LLM (or built-in **mock** for local) builds a DAG of tool/agent steps.
- **Multi-agent helpers:** route, delegate, fan-out, critic, and consensus tools included.
- **Optional RAG:** Postgres + pgvector + embedding tools & endpoints.
- **Prod-ready pieces:** multi-tenant keys, Redis/Celery, Prometheus, OTEL, Sentry hooks.

---

## Table of Contents

- [TL;DR Quick Start](#tldr-quick-start)
- [Architecture (for engineers)](#architecture-for-engineers)
- [Component Deep Dive](#component-deep-dive)
  - [1) HTTP API Layer](#1-http-api-layer)
  - [2) Tool System](#2-tool-system)
  - [3) Planner](#3-planner)
  - [4) Multi-Agent Utilities](#4-multi-agent-utilities)
  - [5) RAG Subsystem (optional)](#5-rag-subsystem-optional)
  - [6) Persistence & Tenancy](#6-persistence--tenancy)
  - [7) Background Workers](#7-background-workers)
  - [8) Observability](#8-observability)
  - [9) Security Notes](#9-security-notes)
- [How Users Use It (with HTTP from Python)](#how-users-use-it-with-http-from-python)
- [Implementer’s Guide (code snippets)](#implementers-guide-code-snippets)
- [Extending AgentSpring](#extending-agentspring)
- [Roadmap](#roadmap)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## TL;DR Quick Start

```bash
# 1) Configure (multi-tenant recommended)
cat > .env <<'EOF'
API_KEY=
ADMIN_API_KEY=your-admin-key
# Optional for RAG embeddings:
# OPENAI_API_KEY=sk-...
CORS_ALLOWED_ORIGINS=http://localhost:8080
EOF

# 2) Bring the stack up (Postgres, Redis, App)
docker compose up -d --build

# 3) Create a tenant + API key
curl -s -X POST http://localhost:8000/v1/admin/tenants \
  -H "X-Admin-Key: your-admin-key" -H "Content-Type: application/json" \
  -d '{"name":"dev","api_key":"dev-key"}'

# 4) Smoke test
curl -s http://localhost:8000/health
curl -s http://localhost:8000/v1/tools -H "X-API-Key: dev-key"

# 5) Ask the planner for a workflow (mock provider)
curl -s -X POST http://localhost:8000/v1/agents/run \
  -H "X-API-Key: dev-key" -H "Content-Type: application/json" \
  -d '{"prompt":"Use math_eval to compute 2+2","provider":"mock","stream":false}'
```

---

## Architecture (for engineers)

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                         Client                          │
                    │     (Web, Python, CLI) — Talks HTTP to AgentSpring      │
                    └─────────────▲───────────────────────────────────────────┘
                                  │
                                  │ HTTP
                                  │
┌─────────────────────────────────┴────────────────────────────────────────────────┐
│                                  AgentSpring                                     │
│                                                                                  │
│  FastAPI                                                                         │
│  ┌───────────────────────────────────────────────────────────────────────────┐   │
│  │  /v1/agents/run  — plan (and optionally execute) agentic workflows       │   │
│  │  /v1/tools/{tool} — dynamic tool invocation (sync/async)                 │   │
│  │  /v1/tools        — list tools                                           │   │
│  │  /v1/admin/*      — multi-tenant admin                                   │   │
│  └───────────────────────────────────────────────────────────────────────────┘   │
│           │                             │                                         │
│           │ uses                        │ registers                                │
│           ▼                             ▼                                         │
│  Planner (LLM or mock)        Tool Registry (decorator + registry object)         │
│  • Builds DAG plan            • Exposes schemas to planner                         │
│  • Multi-agent aware          • Handles sync/async tools                           │
│                                                                                  │
│    ┌──────────────┐    ┌──────────────┐   ┌──────────────┐   ┌─────────────────┐ │
│    │ delegate     │    │ router       │   │ critic       │   │ consensus       │ │
│    │ (sub-agent)  │    │ (route)      │   │ review       │   │ merge/fan-out   │ │
│    └──────────────┘    └──────────────┘   └──────────────┘   └─────────────────┘ │
│                                                                                  │
│ RAG (optional)                                                                   │
│  • Embedding tools -> Postgres+pgvector                                          │
│  • /v1/collections/* for upsert/search                                           │
│                                                                                  │
│ Persistence & Infra                                                              │
│  • Postgres (runs, tenants, embeddings...)                                       │
│  • Redis + Celery for background tasks                                           │
│  • Prometheus /metrics, Sentry, OTEL                                             │
└──────────────────────────────────────────────────────────────────────────────────┘
```

**Why these pieces exist (benefits):**

- **Dynamic tools** decouple “capabilities” from “planning”. Extend by importing a file—no service rewrites.
- **Planner consumes tool schemas** (OpenAI-tool-style) so the LLM plans _valid_ steps with explicit parameters.
- **Sync/async tool support** lets you wrap DB calls, network I/O, or CPU helpers without blocking the event loop.
- **Delegate/router/critic/consensus** package common multi-agent patterns into reusable, testable building blocks.
- **Multi-tenant** keys + DB enable SaaS-style isolation and auditability.
- **RAG** is first-class (optional), attaching knowledge to agents using the same API surface.
- **Observability** (Prometheus/Sentry/OTEL) is built-in, crucial for production debugging and scaling.

---

## Component Deep Dive

### 1) HTTP API Layer

- **FastAPI** app with middleware:
  - **CORS**, **agent depth** (prevents infinite recursion), **Prometheus** metrics.
- **Dynamic tool endpoint:** `POST /v1/tools/{name}`
  - Reflects the target callable’s signature and injects caller headers only if supported (`__caller_headers__` or `**kwargs`).
  - Runs **async tools directly**; runs **sync tools** via a thread pool (`anyio.to_thread.run_sync`) so the event loop is never blocked.
  - Signature mismatches → **HTTP 400** with precise messages.
- **Agent planning endpoint:** `POST /v1/agents/run`
  - Builds a **DAG plan** from an LLM (or mock provider for local).
  - Persists a **Run** row with `tenant_id` (UUID) in multi-tenant mode.
  - Default behavior is **plan-only** (client executes). Server-side execution is easy to enable (see [Extending](#extending-agentspring)).

**Benefit:** Clean, stable API; safe tool invocation; key propagation for internal delegation; robust async behavior.

---

### 2) Tool System

- **Decorator:** `@tool(name, description, parameters=JSONSchema)` registers a callable and its schema.
- **Registry (`ToolRegistry`):**
  - Dict-like (`get/keys/items`) plus schema store.
  - `to_openai_functions()` for planners that expect OpenAI tool format.
  - `registry` alias for legacy dict-style access.
- **Auto-import**: import tool modules on app start to populate the registry.
- **Sync/async** supported; dynamic route dispatches correctly.

**Benefit:** Engineers add capabilities with near-zero ceremony. Planners “see” new tools immediately via schemas.

---

### 3) Planner

- Contract: `plan_async(prompt, ...) -> plan_json` where plan is a **DAG**:

  ```json
  {
    "workflow_id": "…",
    "name": "ad-hoc",
    "nodes": [
      {"id":"n1","type":"tool","tool":"math_eval","args":{"expr":"2+2"},"depends_on":[]}
    ]
  }
  ```

- Uses `tools.to_openai_functions()` so the LLM plans **valid** tool calls.
- **Providers:** “mock” (deterministic), OpenAI, Azure OpenAI, Anthropic (select per request).
- **Multi-agent aware:** helper tools enable sub-agent delegation, routing, critique, and consensus.

**Benefit:** Separation of concerns: “what to do” (planning) vs. “how to do it” (tools). Swap providers or prompt logic without touching tools.

---

### 4) Multi-Agent Utilities

- `delegate_agent` → calls `/v1/agents/run` under-the-hood, **forwarding the caller’s API key**.
- `agent_router` / `route_and_delegate` → route task to a named agent or strategy.
- `fanout_delegate` / `fanout_and_consensus` → run multiple assistants in parallel, then merge.
- `critic_review` → critique a response for quality/completeness.
- `consensus_merge` → deduplicate/merge strings by similarity or simple voting.

**Benefit:** Encodes proven multi-agent patterns, so your plans are expressive without bespoke orchestration glue.

---

### 5) RAG Subsystem (optional)

- **Schema:** `embeddings(collection, doc_id, text, vector, metadata, tenant_id)` with a unique `(tenant_id, collection, doc_id)`.
- **Tools:** `embed_text`, `rag_upsert`, `rag_retrieve`.
- **REST:** `/v1/collections/{name}/docs` and `/v1/collections/{name}/search` for convenience.

**Benefit:** Keep domain knowledge next to your agents; standard API surface for planning + retrieval.

---

### 6) Persistence & Tenancy

- **Postgres** for runs, tenants, embeddings, etc.
- **Single-tenant** (dev): set `API_KEY`; all requests must send that key.
- **Multi-tenant** (recommended): leave `API_KEY` blank; set `ADMIN_API_KEY` and use `POST /v1/admin/tenants` to issue per-tenant keys.

**Benefit:** SaaS-ready isolation with smooth progression from dev to prod.

---

### 7) Background Workers

- **Redis + Celery** for long-running jobs and fan-out work you don’t want on the request path.
- Offload RAG ingestion, crawling, evaluators, bulk workflows.

**Benefit:** Keep HTTP latency low; scale horizontally.

---

### 8) Observability

- **Prometheus**: `/metrics` middleware with labels & histograms.
- **Sentry**: set `SENTRY_DSN` for error tracking.
- **OTEL**: set `OTEL_EXPORTER_OTLP_ENDPOINT` for traces/spans.

**Benefit:** First-class production telemetry for debugging and capacity planning.

---

### 9) Security Notes

- **Key propagation:** dynamic tool route forwards caller headers _only_ when the tool supports `__caller_headers__` (or `**kwargs`).
- **SSRF protection:** add allow/deny lists for HTTP tools; proxy or sandbox in production.
- **CORS:** restrict origins in prod; avoid `*`.
- **Rate limiting / allowlists:** middleware hooks included.

---

## How Users Use It (with HTTP from Python)

A typical user **does not** call tools manually. They provide a goal; AgentSpring plans a DAG; the server or client executes it.

Below is a client that (1) asks for a plan, (2) executes the DAG by calling `/v1/tools/{tool}`, (3) passes results between nodes.

```python
# examples/agent_workflow_demo.py
import os, json, requests
from collections import deque

BASE = os.getenv("AGENTSPRING_BASE_URL", "http://localhost:8000")
KEY  = os.getenv("AGENTSPRING_API_KEY", "dev-key")
PROV = os.getenv("AGENTSPRING_PROVIDER", "mock")
H = {"X-API-Key": KEY, "Content-Type": "application/json", "Accept": "application/json"}

def req(m, path, body=None):
    r = requests.request(m, f"{BASE}{path}", headers=H, json=body, timeout=60)
    r.raise_for_status()
    return r.json() if r.text else None

def plan(prompt):
    return req("POST", "/v1/agents/run", {"prompt": prompt, "provider": PROV, "stream": False})

def call(tool, args):
    return req("POST", f"/v1/tools/{tool}", args)["output"]

def topo(nodes):
    indeg={n["id"]:0 for n in nodes}; g={n["id"]:[] for n in nodes}; by={n["id"]:n for n in nodes}
    for n in nodes:
        for d in n.get("depends_on", []): indeg[n["id"]]+=1; g[d].append(n["id"])
    from collections import deque
    q=deque([i for i,d in indeg.items() if d==0]); out=[]
    while q:
        u=q.popleft(); out.append(by[u])
        for v in g[u]:
            indeg[v]-=1
            if indeg[v]==0: q.append(v)
    if len(out)!=len(nodes): raise RuntimeError("Cycle in plan")
    return out

def resolve(args, results):
    r={}
    for k,v in (args or {}).items():
        r[k]=results.get(v[2:-1]) if isinstance(v,str) and v.startswith("${") and v.endswith("}") else v
    return r

def execute(plan):
    res={}; order=topo(plan.get("nodes", []))
    for n in order:
        if n["type"]=="tool":
            out = call(n["tool"], resolve(n.get("args"), res))
            res[n["id"]] = out
            print(f"[tool:{n['tool']}] -> {out}")
        elif n["type"]=="agent":
            out = call("call_named_agent", resolve(n.get("args"), res))
            res[n["id"]] = out
            print(f"[agent] -> {out}")
    return res

if __name__ == "__main__":
    goal = "Use math_eval to compute 2+2, then run a critic review on the result."
    p = plan(goal)
    result = p.get("result") or execute(p["plan"])
    print("\nFINAL:", json.dumps(result, indent=2))
```

Run:

```bash
export AGENTSPRING_BASE_URL=http://localhost:8000
export AGENTSPRING_API_KEY=dev-key
export AGENTSPRING_PROVIDER=mock
python examples/agent_workflow_demo.py
```

---

## Implementer’s Guide (code snippets)

### Tool registration

```python
# agentspring/tools/__init__.py (core excerpt)
from typing import Callable, Awaitable, Any, Dict, List

_fn_map: Dict[str, Callable[..., Awaitable[Any]]] = {}
_schema_map: Dict[str, dict] = {}

class ToolRegistry:
    def __init__(self, fn_map=None, schema_map=None):
        self._fns = fn_map or _fn_map
        self._schemas = schema_map or _schema_map
        self.registry = self
        self.schemas = self._schemas

    def get(self, name): return self._fns.get(name)
    def keys(self): return self._fns.keys()
    def items(self): return self._fns.items()
    def __getitem__(self, k): return self._fns[k]
    def as_schemas(self): return dict(self._schemas)

    def to_openai_functions(self) -> List[dict]:
        return [{"type":"function","function":{
            "name": s.get("name", n),
            "description": s.get("description",""),
            "parameters": s.get("parameters", {"type":"object","properties":{},"required":[]})
        }} for n,s in self._schemas.items()]

registry = ToolRegistry()  # exposed as 'tool_registry' in some code paths
tool_registry = registry   # alias for compatibility

def tool(name: str, description: str="", parameters: dict|None=None):
    def _wrap(fn):
        _fn_map[name] = fn
        _schema_map[name] = {
            "name": name, "description": description,
            "parameters": parameters or {"type":"object","properties":{},"required":[]},
        }
        return fn
    return _wrap
```

### Dynamic tool endpoint (sync/async + selective header injection)

```python
# agentspring/api.py (excerpt)
import inspect
from inspect import Parameter
from anyio import to_thread
from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.responses import JSONResponse
from .tools import registry as tool_registry

app = FastAPI()

@app.post("/v1/tools/{name}")
async def call_tool(name: str, request: Request, payload: dict = Body(...)):
    fn = tool_registry.get(name)
    if not fn:
        raise HTTPException(404, f"Unknown tool '{name}'")

    caller_headers = {"X-API-Key": request.headers.get("x-api-key")}
    params = inspect.signature(fn).parameters
    accepts_var_kw = any(p.kind == Parameter.VAR_KEYWORD for p in params.values())

    kwargs = dict(payload or {})
    if "__caller_headers__" in params or accepts_var_kw:
        kwargs["__caller_headers__"] = caller_headers

    try:
        if inspect.iscoroutinefunction(fn):
            result = await fn(**kwargs)  # async tool
        else:
            result = await to_thread.run_sync(lambda: fn(**kwargs))  # sync tool
    except TypeError as e:
        raise HTTPException(400, f"Bad args for '{name}': {e}")

    return JSONResponse({"tool": name, "output": result})
```

### Example tools

```python
# agentspring/tools/builtin_math.py
from . import tool

@tool(
  "math_eval",
  "Evaluate arithmetic like '12*(3+4)'.",
  parameters={"type":"object","properties":{"expr":{"type":"string"}},"required":["expr"]}
)
def math_eval(expr: str, **_):
    import ast, operator as op
    ops = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, ast.Pow: op.pow, ast.USub: op.neg}
    def eval_(node):
        if isinstance(node, ast.Num): return node.n
        if isinstance(node, ast.UnaryOp): return ops[type(node.op)](eval_(node.operand))
        if isinstance(node, ast.BinOp): return ops[type(node.op)](eval_(node.left), eval_(node.right))
        raise ValueError("Unsupported")
    return eval_(ast.parse(expr, mode="eval").body)
```

```python
# agentspring/tools/delegate.py
import httpx
from typing import Optional, Dict
from . import tool
from ..config import settings

@tool(
  "delegate_agent",
  "Delegate a prompt to a sub-agent via /v1/agents/run",
  parameters={
    "type":"object",
    "properties":{"prompt":{"type":"string"},"provider":{"type":"string"},"stream":{"type":"boolean"}},
    "required":["prompt","provider"]
  }
)
async def delegate_agent(prompt: str, provider: str="mock", stream: bool=False,
                         __caller_headers__: Optional[Dict[str,str]] = None):
    api_key = (__caller_headers__ or {}).get("X-API-Key") or (settings.API_KEY or "").strip()
    if not api_key:
        raise RuntimeError("No tenant API key available for delegation.")
    headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post("http://127.0.0.1:8000/v1/agents/run", headers=headers,
                              json={"prompt": prompt, "provider": provider, "stream": bool(stream)})
        r.raise_for_status()
        return r.json()
```

---

## Extending AgentSpring

- **Server-side executor:** after planning in `/v1/agents/run`, execute the DAG on the server and return `{"result": ...}`. Reuse the topo logic from the client example; call tools directly via the registry to avoid HTTP hops.
- **New tools:** drop a module under `agentspring/tools/` and import it once at startup.
- **New providers:** create an adapter with `complete(prompt, tools_schemas, ...)`; register it by name; clients pass `"provider": "<name>"`.
- **Policies:** allow/deny lists for network/file tools; per-tenant timeouts, concurrency limits, quotas.
- **UI:** extend the included console (in `docker-compose.yml`) to visualize runs, nodes, and outputs.

---

## Roadmap

**Short-term**
- Plan-and-execute mode in `/v1/agents/run` (config + payload flag).
- Workflow templates: persisted, versioned DAGs with parameterization.
- Retry & circuit breakers per tool; deadlines; cancellation propagation.
- Per-tenant quotas & budgets; token/cost metering by provider.
- Richer arg interpolation: `${node.key}`, JSONPath, Jinja templates.
- Tool telemetry: latency histograms, success rates, cost per invocation.

**Mid-term**
- Agent registry with skills, memory, and profiles; agent↔agent messaging inbox.
- Sandboxing for risky tools (network/fs) using Firecracker/OCI isolation.
- Policy engine (OPA/Cedar) for RBAC, data boundaries, tool access rules.
- Evaluator harness: golden tasks, pass@k, auto-eval via Celery + Prometheus.
- Streaming: SSE/gRPC for token streams and live node telemetry.

**Long-term**
- Federated planning across services; sharded tool registries.
- Stateful workflows with resumability and exactly-once guarantees.
- Knowledge routing across multiple RAG stores; hybrid search; citation graphs.
- Marketplace for third-party tools/agents with billing & sandbox constraints.

---

## Troubleshooting

- **401 Invalid API key**  
  Send `X-API-Key` matching single-tenant `API_KEY` or a created tenant’s key.

- **UUID error on runs**  
  Use multi-tenant mode (create a tenant) so `tenant_id` is a real UUID; or synthesize a UUID in dev.

- **“object float can’t be used in await expression”**  
  Your tool is sync; the dynamic route now detects sync vs async and runs sync tools in a thread.

- **Delegate tool 500**  
  Ensure the dynamic route passes `__caller_headers__` only if supported, and `delegate_agent` forwards `X-API-Key`.

- **Docker port unreachable**  
  Ensure Uvicorn binds `0.0.0.0:8000` and compose maps `8000:8000`.

---

## License

This repository is open source. See `LICENSE` for details.
