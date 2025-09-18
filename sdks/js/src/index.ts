export type AgentEvent = { type: string; [k: string]: any };
export class AgentSpringClient {
  baseUrl: string; apiKey: string; bearer?: string;
  constructor(baseUrl: string, apiKey: string, bearer?: string){ this.baseUrl = baseUrl.replace(/\/$/, ""); this.apiKey = apiKey; this.bearer = bearer; }
  async run(prompt: string, provider = "openai"){
    const r = await fetch(`${this.baseUrl}/v1/agents/run`, { method: "POST", headers: { "Content-Type":"application/json", "X-API-Key": this.apiKey, ...(this.bearer?{"Authorization":`Bearer ${this.bearer}`}:{}) }, body: JSON.stringify({ prompt, provider, stream: false }) });
    if (!r.ok) throw new Error(await r.text()); return r.json();
  }
  async *stream(prompt: string, provider="openai"){
    const r = await fetch(`${this.baseUrl}/v1/agents/run`, { method: "POST", headers: { "Content-Type":"application/json", "X-API-Key": this.apiKey, "Accept":"text/event-stream", ...(this.bearer?{"Authorization":`Bearer ${this.bearer}`}:{}) }, body: JSON.stringify({ prompt, provider, stream: true }) });
    if (!r.ok || !r.body) throw new Error(await r.text());
    const reader = r.body.getReader(); const decoder = new TextDecoder();
    while(true){ const {value, done} = await reader.read(); if (done) break; const chunk = decoder.decode(value, {stream:true}); for (const line of chunk.split("\n")) if (line.startsWith("data: ")) yield JSON.parse(line.slice(6)); }
  }
  async upsertDoc(collection: string, docId: string, text: string, metadata: any = {}){
    const r = await fetch(`${this.baseUrl}/v1/collections/${collection}/docs`, { method: "POST", headers: { "Content-Type":"application/json", "X-API-Key": this.apiKey, ...(this.bearer?{"Authorization":`Bearer ${this.bearer}`}:{}) }, body: JSON.stringify({ doc_id: docId, text, metadata }) });
    if (!r.ok) throw new Error(await r.text()); return r.json();
  }
  async search(collection: string, q: string, k = 5){
    const u = new URL(`${this.baseUrl}/v1/collections/${collection}/search`); u.searchParams.set("q", q); u.searchParams.set("k", String(k));
    const r = await fetch(u, { headers: { "X-API-Key": this.apiKey, ...(this.bearer?{"Authorization":`Bearer ${this.bearer}`}:{}) } });
    if (!r.ok) throw new Error(await r.text()); return r.json();
  }
}
