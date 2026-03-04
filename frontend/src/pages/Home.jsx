import React from "react";
export default function Home(){
  return (
    <div>
      <h1>Welcome</h1>
      <img src="https://placekitten.com/800/300" alt="hero" style={{maxWidth:'100%'}}/>
      <p>Use "Ask (Node/Ollama)" to ask the local Ollama model. Use "Analyze (Python)" to run the step-by-step analysis pipeline.</p>
    </div>
  )
}