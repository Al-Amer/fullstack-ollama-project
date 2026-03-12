from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import traceback
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from spellchecker import SpellChecker

# Download nltk resources
nltk.download('punkt')
nltk.download('stopwords')

app = FastAPI()

# Tools
spell = SpellChecker()
stop_words = set(stopwords.words("english"))
vectorizer = TfidfVectorizer()
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Q(BaseModel):
    question: str


# CLEANING
def clean_text(text: str):
    print("\n========== CLEANING STEP ==========")
    text = text.strip()
    text = re.sub(r'[\r\n]+', ' ', text)
    text = re.sub(r'[^0-9a-zA-Z\s\?\.,]', '', text)
    text = text.lower()
    print("Cleaned:", text)
    return text


# TOKENIZATION
def tokenize(text):
    print("\n========== TOKENIZATION STEP ==========")
    tokens = word_tokenize(text)
    print("Tokens:", tokens)
    return tokens

# QUESTION DETECTION 
def detect_question_type(text, tokens):
    print("\n========== QUESTION TYPE CHECK ==========")
    question_words = ["what","why","how","when","where","who","which"]
    aux_verbs = ["is","are","do","does","did","can","could","should","would","will"]
    if text.endswith("?"):
        return True
    if any(q in tokens for q in question_words):
        return True
    if tokens and tokens[0] in aux_verbs:
        return True
    return False

# SPELL CHECK 
def check_spelling(tokens):
    print("\n========== SPELL CHECK ==========")
    misspelled = spell.unknown(tokens)
    corrections = {}
    for word in misspelled:
        corrections[word] = spell.correction(word)
    print("Misspelled:", corrections)
    return corrections

# VALIDATION 
def validate_question(text, tokens):
    print("\n========== QUESTION VALIDATION ==========")
    problems = []
    if len(tokens) < 3:
        problems.append("Question too short")
    if all(t.isdigit() for t in tokens):
        problems.append("Question contains only numbers")
    if not re.search(r'[a-zA-Z]', text):
        problems.append("Question has no real words")
    return problems

# COMPLETENESS CHECK
def check_question_completeness(tokens):
    print("\n========== COMPLETENESS CHECK ==========")
    meaningful = [t for t in tokens if t not in stop_words and len(t) > 3]
    if len(meaningful) < 2:
        return False, "Not enough meaningful words"
    vague_words = ["it","this","that","thing","stuff"]
    if any(w in tokens for w in vague_words):
        return False, "Question contains vague references"
    return True, "Question seems complete"

# IMPROVEMENT 
def improve_question(tokens):
    print("\n========== QUESTION IMPROVEMENT ==========")
    question = " ".join(tokens)
    if not question.endswith("?"):
        question += "?"
    print("Improved:", question)
    return question

#  INTENT DETECTION 
def detect_intent(tokens):
    print("\n========== INTENT DETECTION ==========")
    if "how" in tokens:
        return "how-to"
    if "what" in tokens:
        return "definition"
    if "why" in tokens:
        return "explanation"
    if "calculate" in tokens or any(t.isdigit() for t in tokens):
        return "calculation"
    return "unknown"

# API ENDPOINT
@app.post("/analyze")
async def analyze(q: Q):
    try:
        print("\n\n===== NEW REQUEST =====")
        original = q.question
        print("Original:", original)
        # 1 CLEAN
        cleaned = clean_text(original)
        # 2 TOKENIZE
        tokens = tokenize(cleaned)
        # 3 QUESTION TYPE
        is_question = detect_question_type(cleaned, tokens)
        if not is_question:
            return {
                "status": "not_a_question",
                "message": "Input looks like a normal sentence."
            }
        # 4 SPELL CHECK
        spelling_errors = check_spelling(tokens)
        # 5 VALIDATION
        problems = validate_question(cleaned, tokens)
        if problems:
            return {
                "status": "bad_question",
                "problems": problems
            }
        # 6 TF-IDF
        print("\n========== TF-IDF ==========")
        tfidf_matrix = vectorizer.fit_transform([cleaned])
        tfidf = tfidf_matrix.toarray()

        # 7 EMBEDDING
        print("\n========== EMBEDDING ==========")
        embedding = embed_model.encode(cleaned)

        # 8 COMPLETENESS
        complete, message = check_question_completeness(tokens)
        if not complete:
            return {
                "status": "incomplete_question",
                "message": message
            }
        # 9 EMBEDDING
        print("\n========== EMBEDDING ==========")
        # embedding = embed_model.encode(cleaned)
        embedding = embed_model.encode(cleaned)
        print("Embedding length:", len(embedding))
        print("First 10 values:", embedding[:10])
        # 10 INTENT
        intent = detect_intent(tokens)
        # 11 SEMANTICS
        semantics = {
            "length": len(tokens),
            "contains_question_mark": "?" in original,
            "keywords": tokens[:5]
        }
        print("\n========== DONE ==========")
        return {
            "status": "ok",
            "original": original,
            "cleaned": cleaned,
            "tokens": tokens,
            "spelling_errors": spelling_errors,
            "improved_question": improved_question,
            "tfidf": tfidf.tolist(),
            "tfidf_shape": tfidf.shape,
            "embedding_dimension": len(embedding),
            "intent": intent,
            "semantics": semantics
        }
    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()
        return {"error": str(e)}