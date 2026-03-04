import React from "react";
import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import NodePage from "./pages/NodePage";
import PythonPage from "./pages/PythonPage";

export default function App(){
  return (
    <>
      <Navbar />
      <div style={{padding:20}}>
        <Routes>
          <Route path="/" element={<Home/>}/>
          <Route path="/node" element={<NodePage/>}/>
          <Route path="/python" element={<PythonPage/>}/>
        </Routes>
      </div>
    </>
  )
}