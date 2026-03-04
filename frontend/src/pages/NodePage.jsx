import React, { useState } from "react";
import axios from "axios";

export default function NodePage(){
  const [q, setQ] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(){
    setLoading(true);
    try{
      const res = await axios.post("http://localhost:8000/ask", { question: q });
      setAnswer(res.data.answer || JSON.stringify(res.data));
    }catch(e){
      setAnswer("Error: "+(e.response?.data?.error || e.message));
    }finally{ setLoading(false);}
  }

  return (
    <div>
      <h2>Ask Ollama (via Node backend)</h2>
      <textarea value={q} onChange={e=>setQ(e.target.value)} rows={4} style={{width:'100%'}}/>
      <div style={{marginTop:8}}>
        <button onClick={submit} disabled={loading || !q}>Send to Node/Ollama</button>
      </div>
      <pre style={{whiteSpace:'pre-wrap', marginTop:12}}>{loading ? "Loading..." : answer}</pre>
    </div>
  )
}