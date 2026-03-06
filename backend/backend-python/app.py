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

# =================================
# STEP 3 — QUESTION VALIDATION
# =================================
def validate_question(text, tokens):

    print("\n========== QUESTION VALIDATION ==========")

    problems = []

    if len(tokens) < 3:
        problems.append("Question is too short")

    if all(t.isdigit() for t in tokens):
        problems.append("Question contains only numbers")

    if not re.search(r'[a-zA-Z]', text):
        problems.append("Question has no real words")

    question_words = ["what","why","how","when","where","who","which"]

    if not any(q in tokens for q in question_words):
        problems.append("No question word detected")

    if problems:
        print("Problems detected:")
        for p in problems:
            print("-", p)
    else:
        print("Question looks good")

    return problems


# =================================
# STEP 4 — QUESTION IMPROVEMENT
# =================================
def improve_question(tokens):

    print("\n========== QUESTION IMPROVEMENT ==========")

    if "why" in tokens:
        improved = "why " + " ".join(tokens) + "?"
        print("Improved question:", improved)
        return improved

    if "how" in tokens:
        improved = "how " + " ".join(tokens) + "?"
        print("Improved question:", improved)
        return improved

    return " ".join(tokens)

# =================================
# API ENDPOINT
# =================================
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

        # Step 3
        problems = validate_question(cleaned, tokens)

        if problems:
            return {
                "status": "bad_question",
                "original": original,
                "cleaned": cleaned,
                "tokens": tokens,
                "problems": problems,
                "suggestion": "Please ask a clearer question."
            }

        # STEP 4
        improved_question = improve_question(tokens)

        # STEP 5 — TF-IDF
        print("\n========== TF-IDF STEP ==========")

        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform([cleaned]).toarray()
        print("TF-IDF vector:", tfidf)
        print("TF-IDF shape:", tfidf.shape)

        # STEP 6 — EMBEDDINGS
        print("\n========== EMBEDDING STEP ==========")
        embedding = embed_model.encode(cleaned)
        print("Embedding length:", len(embedding))
        print("First 10 values:", embedding[:10])

        # STEP 7 — INTENT DETECTION
        print("\n========== INTENT DETECTION ==========")
        intent = "unknown"
        if "how" in tokens:
            intent = "how-to"
        elif "what" in tokens:
            intent = "definition"
        elif "why" in tokens:
            intent = "explanation"
        elif "calculate" in tokens or any(t.isdigit() for t in tokens):
            intent = "calculation"
        print("Detected intent:", intent)

       # STEP 8 — SEMANTIC ANALYSIS
        print("\n========== SEMANTIC ANALYSIS ==========")
        semantics = {
            "length": len(tokens),
            "contains_question_mark": '?' in original,
            "top_tokens": tokens[:5]
        }
        print(f"Semantic Info: {semantics}")

        print("\n========== PROCESS COMPLETE ==========\n")

        return {
            "status": "ok",
            "original": original,
            "cleaned": cleaned,
            "tokens": tokens,
            "improved_question": improved_question,
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