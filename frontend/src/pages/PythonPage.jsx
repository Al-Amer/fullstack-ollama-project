import React, { useState } from "react";
import axios from "axios";

export default function PythonPage(){
  const [q, setQ] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  async function submit(){
    setLoading(true);
    try{
      const res = await axios.post("http://localhost:8001/analyze", { question: q });
      setResult(res.data);
    }catch(e){
      setResult({ error: e.response?.data || e.message });
    }finally{ setLoading(false);}
  }

  return (
    <div>
      <h2>Analyze (Python)</h2>
      <textarea value={q} onChange={e=>setQ(e.target.value)} rows={4} style={{width:'100%'}}/>
      <div style={{marginTop:8}}>
        <button onClick={submit} disabled={loading || !q}>Analyze in Python</button>
      </div>
      <pre style={{whiteSpace:'pre-wrap', marginTop:12}}>{loading ? "Working..." : JSON.stringify(result, null, 2)}</pre>
    </div>
  )
}
