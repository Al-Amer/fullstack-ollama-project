from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import traceback
import re
import nltk
from nltk.tokenize import word_tokenize
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer

nltk.download('punkt')

app = FastAPI()

# ✅ CORS MUST BE ADDED RIGHT AFTER app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development
    allow_credentials=True,
    allow_methods=["*"],  # allow OPTIONS
    allow_headers=["*"],
)

embed_model = SentenceTransformer('all-MiniLM-L6-v2')

class Q(BaseModel):
    question: str

# ===============================
# STEP 1 — CLEANING
# ===============================
def clean_text(text: str) -> str:
    print("\n========== CLEANING STEP ==========")

    text = text.strip()
    print(f"After strip: {text}")

    text = re.sub(r'[\r\n]+', ' ', text)
    print(f"After removing new lines: {text}")

    text = re.sub(r'[^0-9a-zA-Z\s\?\.,]', '', text)
    print(f"After removing symbols: {text}")

    text = text.lower()
    print(f"After lowercase: {text}")

    return text


# ===============================
# STEP 2 — TOKENIZATION
# ===============================
def tokenize(text: str):
    print("\n========== TOKENIZATION STEP ==========")
    tokens = word_tokenize(text)
    print(f"Tokens: {tokens}")
    return tokens


@app.post("/analyze")
async def analyze(q: Q):
    try:
        print("\n\n==============================")
        print("NEW REQUEST RECEIVED")
        print("==============================")

        original = q.question
        print(f"\nOriginal text: {original}")

        # Step 1
        cleaned = clean_text(original)

        # Step 2
        tokens = tokenize(cleaned)

        # Step 3 — TF-IDF
        print("\n========== TF-IDF STEP ==========")
        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform([cleaned]).toarray()
        print(f"TF-IDF Vector: {tfidf}")
        print(f"TF-IDF Shape: {tfidf.shape}")

        # Step 4 — Embeddings
        print("\n========== EMBEDDING STEP ==========")
        embedding = embed_model.encode(cleaned)
        print(f"Embedding vector length: {len(embedding)}")
        print(f"First 10 embedding values: {embedding[:10]}")

        # Step 5 — Intent Detection
        print("\n========== INTENT DETECTION STEP ==========")
        intent = "unknown"

        if cleaned.startswith("how") or "how" in tokens:
            intent = "how-to"
            print("Detected 'how' → intent = how-to")

        elif cleaned.startswith("what") or "what" in tokens:
            intent = "definition"
            print("Detected 'what' → intent = definition")

        elif cleaned.startswith("why") or "why" in tokens:
            intent = "explanation"
            print("Detected 'why' → intent = explanation")

        elif "calculate" in tokens or any(t.isdigit() for t in tokens):
            intent = "calculation"
            print("Detected number → intent = calculation")

        print(f"Final Intent: {intent}")

        # Step 6 — Semantic info
        print("\n========== SEMANTIC ANALYSIS STEP ==========")
        semantics = {
            "length": len(tokens),
            "contains_question_mark": '?' in original,
            "top_tokens": tokens[:5]
        }
        print(f"Semantic Info: {semantics}")

        print("\n========== PROCESS COMPLETE ==========\n")

        return {
            "original": original,
            "cleaned": cleaned,
            "tokens": tokens,
            "tfidf": tfidf.tolist(),
            "embedding_dim": len(embedding),
            "intent": intent,
            "semantics": semantics,
            "final_answer": f"Detected intent: {intent}. Tokens: {len(tokens)}."
        }
    except Exception as e:
        print("ERROR in /analyze:", e)
        traceback.print_exc()
        return {"error": str(e)}