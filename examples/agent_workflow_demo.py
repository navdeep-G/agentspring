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
