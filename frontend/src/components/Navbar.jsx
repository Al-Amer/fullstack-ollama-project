import React from "react";
import { Link } from "react-router-dom";

export default function Navbar(){
  return (
    <nav style={{display:'flex',gap:16,padding:12,background:'#eee'}}>
      <Link to="/">Home</Link>
      <Link to="/node">Ask (Node/Ollama)</Link>
      <Link to="/python">Analyze (Python)</Link>
    </nav>
  )
}