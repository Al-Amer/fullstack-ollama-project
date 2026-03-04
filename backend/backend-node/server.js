const express = require('express');
const axios = require('axios');
const cors = require('cors');

const app = express();
app.use(express.json());
app.use(cors());

const OLLAMA_URL = "http://localhost:11434/api/generate";

app.post('/ask', async (req, res) => {
  const { question } = req.body;

  if (!question) {
    return res.status(400).json({ error: "Question is required" });
  }

  try {
    const response = await axios.post(OLLAMA_URL, {
      model: "llama3.2:latest",   // change if needed
      prompt: question,
      stream: false
    });

    res.json({
      answer: response.data.response
    });

  } catch (error) {
    console.error(error.message);
    res.status(500).json({ error: "Ollama request failed" });
  }
});

app.listen(8000, () => {
  console.log("Node backend running on http://localhost:8000");
});