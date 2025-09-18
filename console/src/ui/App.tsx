import React, { useEffect, useMemo, useState } from 'react'
import AdminPanel from './AdminPanel'
import { makeManager, login, handleRedirect, getToken } from '../auth/oidc'
type RunItem = { id: string; status: string; created_at: string }
export default function App(){
  const [baseUrl, setBaseUrl] = useState(localStorage.getItem("baseUrl") || "http://localhost:8000")
  const [apiKey, setApiKey] = useState(localStorage.getItem("apiKey") || "")
  const [provider, setProvider] = useState(localStorage.getItem("provider") || "openai")
  const [prompt, setPrompt] = useState("Summarize https://example.com in 3 bullets")
  const [events, setEvents] = useState<any[]>([])
  const [runs, setRuns] = useState<RunItem[]>([])
  const [oidcConfig, setOidcConfig] = useState(()=>{
    const raw = localStorage.getItem("oidc")
    return raw ? JSON.parse(raw) : { authority: "", client_id: "", redirect_uri: window.location.origin + "/oidc-callback" }
  })
  const [token, setToken] = useState<string|undefined>()

  const um = useMemo(()=> oidcConfig.authority && oidcConfig.client_id ? makeManager(oidcConfig) : null, [oidcConfig])

  useEffect(()=>{ localStorage.setItem("baseUrl", baseUrl) }, [baseUrl])
  useEffect(()=>{ localStorage.setItem("apiKey", apiKey) }, [apiKey])
  useEffect(()=>{ localStorage.setItem("provider", provider) }, [provider])
  useEffect(()=>{ localStorage.setItem("oidc", JSON.stringify(oidcConfig)) }, [oidcConfig])

  useEffect(()=>{
    if (window.location.pathname.endsWith("/oidc-callback") && um){
      handleRedirect(um).then(async _ => { const tok = await getToken(um); setToken(tok || undefined); window.history.replaceState({}, "", "/") })
    } else if (um){ getToken(um).then(tok=> setToken(tok || undefined)) }
  }, [um])

  async function run(){
    setEvents([])
    const resp = await fetch(`${baseUrl}/v1/agents/run`, {
      method: "POST",
      headers: { "Content-Type":"application/json", "X-API-Key": apiKey, "Accept":"text/event-stream", ...(token ? {"Authorization": `Bearer ${token}`} : {}) },
      body: JSON.stringify({ prompt, provider, stream: true })
    })
    if (!resp.ok || !resp.body) { alert(await resp.text()); return }
    const reader = resp.body.getReader(); const decoder = new TextDecoder()
    while(true){
      const {value, done} = await reader.read(); if (done) break
      const chunk = decoder.decode(value, {stream:true})
      for (const line of chunk.split("\n")){
        if (line.startsWith("data: ")){
          try{ const ev = JSON.parse(line.slice(6)); setEvents(prev => [...prev, ev]) }catch{}
        }
      }
    }
    await refreshRuns()
  }

  async function refreshRuns(){
    const r = await fetch(`${baseUrl}/v1/runs`, { headers: { "X-API-Key": apiKey, ...(token ? {"Authorization": `Bearer ${token}`} : {}) } })
    const j = await r.json(); setRuns(j.items || [])
  }
  useEffect(()=>{ refreshRuns() }, [baseUrl, apiKey, token])

  async function upsertDoc(){
    const text = prompt; const collection = "console-docs"
    await fetch(`${baseUrl}/v1/collections/${collection}/docs`, { method: "POST", headers: { "Content-Type":"application/json", "X-API-Key": apiKey, ...(token ? {"Authorization": `Bearer ${token}`} : {}) }, body: JSON.stringify({ doc_id: "note", text }) })
    alert("Upserted the current prompt as a doc into 'console-docs'")
  }

  // Ingestion controls
  const [s3, setS3] = useState({bucket:"", prefix:""})
  const [gcs, setGcs] = useState({bucket:"", prefix:""})
  async function ingestS3(){
    await fetch(`${baseUrl}/v1/collections/console-docs/ingest/s3`, { method: "POST", headers: { "Content-Type":"application/json", "X-API-Key": apiKey, ...(token ? {"Authorization": `Bearer ${token}`} : {}) }, body: JSON.stringify({ bucket: s3.bucket, prefix: s3.prefix }) })
    alert("S3 ingest queued")
  }
  async function ingestGCS(){
    await fetch(`${baseUrl}/v1/collections/console-docs/ingest/gcs`, { method: "POST", headers: { "Content-Type":"application/json", "X-API-Key": apiKey, ...(token ? {"Authorization": `Bearer ${token}`} : {}) }, body: JSON.stringify({ bucket: gcs.bucket, prefix: gcs.prefix }) })
    alert("GCS ingest queued")
  }

  return <div style={{maxWidth: 1100, margin: "0 auto", padding: 24, fontFamily: "system-ui, sans-serif"}}>
    <h2>AgentSpring Console</h2>
    <div style={{display:"grid", gap: 12}}>
      <section style={{display:"grid", gap:8}}>
        <h3>Config</h3>
        <label>Base URL <input value={baseUrl} onChange={e=>setBaseUrl(e.target.value)} style={{width:"100%"}}/></label>
        <label>API Key <input value={apiKey} onChange={e=>setApiKey(e.target.value)} style={{width:"100%"}}/></label>
        <div style={{display:"grid", gridTemplateColumns:"1fr 1fr", gap:8}}>
          <label>Provider
            <select value={provider} onChange={e=>setProvider(e.target.value)} style={{width:"100%"}}>
              <option value="openai">OpenAI</option>
              <option value="azure_openai">Azure OpenAI</option>
              <option value="anthropic">Anthropic</option>
            </select>
          </label>
          <button onClick={()=>refreshRuns()}>Refresh runs</button>
        </div>
        <details>
          <summary>OIDC (optional login)</summary>
          <OIDCPanel/>
        </details>
        <details>
          <summary>Ingestion (S3/GCS)</summary>
          <div style={{display:"grid", gap:8, marginTop:8}}>
            <label>S3 bucket <input value={s3.bucket} onChange={e=>setS3({...s3, bucket: e.target.value})}/></label>
            <label>S3 prefix <input value={s3.prefix} onChange={e=>setS3({...s3, prefix: e.target.value})}/></label>
            <button onClick={ingestS3}>Queue S3 ingest</button>
            <label>GCS bucket <input value={gcs.bucket} onChange={e=>setGcs({...gcs, bucket: e.target.value})}/></label>
            <label>GCS prefix <input value={gcs.prefix} onChange={e=>setGcs({...gcs, prefix: e.target.value})}/></label>
            <button onClick={ingestGCS}>Queue GCS ingest</button>
          </div>
        </details>
      </section>

      <section style={{display:"grid", gap:8}}>
        <h3>Prompt</h3>
        <label>Prompt <textarea value={prompt} onChange={e=>setPrompt(e.target.value)} rows={4} style={{width:"100%"}}/></label>
        <div style={{display:"flex", gap:8}}>
          <button onClick={run}>Run (stream)</button>
          <button onClick={upsertDoc}>Upsert as RAG doc</button>
        </div>
        <div style={{border:"1px solid #ddd", padding: 12, borderRadius: 8, minHeight: 120}}>
          <pre style={{whiteSpace:"pre-wrap"}}>{JSON.stringify(events, null, 2)}</pre>
        </div>
      </section>

      <section>
        <h3>Run Explorer</h3>
        <table style={{width:"100%", borderCollapse:"collapse"}}>
          <thead><tr><th style={{textAlign:"left"}}>ID</th><th>Status</th><th>Created</th></tr></thead>
          <tbody>{runs.map(r => <tr key={r.id} style={{borderTop:"1px solid #eee"}}><td><code>{r.id}</code></td><td>{r.status}</td><td>{new Date(r.created_at).toLocaleString()}</td></tr>)}</tbody>
        </table>
      </section>

      <AdminPanel baseUrl={baseUrl}/>
    </div>
  </div>

  function OIDCPanel(){
    const [cfg, setCfg] = useState(oidcConfig)
    useEffect(()=> setOidcConfig(cfg), [cfg])
    const enabled = cfg.authority && cfg.client_id
    return <div style={{display:"grid", gap:8, marginTop:8}}>
      <label>Authority <input value={cfg.authority} onChange={e=>setCfg({...cfg, authority: e.target.value})}/></label>
      <label>Client ID <input value={cfg.client_id} onChange={e=>setCfg({...cfg, client_id: e.target.value})}/></label>
      <label>Redirect URI <input value={cfg.redirect_uri} onChange={e=>setCfg({...cfg, redirect_uri: e.target.value})}/></label>
      <div>Token: {token ? token.slice(0,20) + "..." : "(not logged in)"} </div>
      <div style={{display:"flex", gap:8}}>
        <button onClick={()=> enabled && login(makeManager(cfg))}>Login</button>
      </div>
    </div>
  }
}
