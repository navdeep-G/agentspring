import React, { useEffect, useState } from 'react'
export default function AdminPanel({baseUrl}:{baseUrl:string}){
  const [adminKey, setAdminKey] = useState(localStorage.getItem("adminKey") || "")
  const [tenants, setTenants] = useState<any[]>([])
  const [form, setForm] = useState({name:"", api_key:""})
  useEffect(()=>{ localStorage.setItem("adminKey", adminKey) }, [adminKey])
  async function listTenants(){
    const r = await fetch(`${baseUrl}/v1/admin/tenants`, { headers: { "X-Admin-Key": adminKey } }); setTenants(await r.json())
  }
  async function createTenant(){
    await fetch(`${baseUrl}/v1/admin/tenants`, { method: "POST", headers: { "X-Admin-Key": adminKey, "Content-Type":"application/json" }, body: JSON.stringify(form) })
    setForm({name:"", api_key:""}); await listTenants()
  }
  return <section style={{marginTop:24}}>
    <h3>Admin (server)</h3>
    <label>Admin Key <input value={adminKey} onChange={e=>setAdminKey(e.target.value)} style={{width:"100%"}}/></label>
    <div style={{display:"flex", gap:8, marginTop:8}}><button onClick={listTenants}>List tenants</button></div>
    <div style={{marginTop:12}}>
      <h4>Create tenant</h4>
      <div style={{display:"grid", gap:8}}>
        <label>Name <input value={form.name} onChange={e=>setForm({...form, name: e.target.value})}/></label>
        <label>API Key <input value={form.api_key} onChange={e=>setForm({...form, api_key: e.target.value})}/></label>
        <button onClick={createTenant}>Create</button>
      </div>
    </div>
    <pre style={{whiteSpace:"pre-wrap"}}>{JSON.stringify(tenants, null, 2)}</pre>
  </section>
}
