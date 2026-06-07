
import torch
import json
import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── Load model on startup ────────────────────────────────────
MODEL_PATH = "./model"

with open(f"{MODEL_PATH}/kaam_config.json", "r") as f:
    config = json.load(f)

KAAM_ID2LABEL = {int(k): v for k, v in config["id2label"].items()}
KAAM_LABEL2ID = config["label2id"]

print("Loading model...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model     = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model  = model.to(device)
model.eval()
print(f"Model loaded on {device} ✓")

# ── FastAPI app ──────────────────────────────────────────────
app = FastAPI(title="KAAM Emotion API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request/Response models ──────────────────────────────────
class EmotionRequest(BaseModel):
    text: str
    user_id: str = "anon"

# ── Predict function ─────────────────────────────────────────
def predict_emotion(text: str) -> dict:
    tokens     = tokenizer(text, truncation=False, padding=False)
    total_tokens = len(tokens["input_ids"])

    if total_tokens <= 128:
        inputs = tokenizer(
            text,
            return_tensors="pt",
            max_length=128,
            padding="max_length",
            truncation=True
        ).to(device)

        with torch.no_grad():
            logits = model(**inputs).logits
            probs  = torch.softmax(logits, dim=-1)[0]

        top_id = torch.argmax(probs).item()
        return {
            "emotion":    KAAM_ID2LABEL[top_id],
            "confidence": round(probs[top_id].item(), 4),
            "all_scores": {
                KAAM_ID2LABEL[i]: round(probs[i].item(), 4)
                for i in range(len(KAAM_ID2LABEL))
            },
            "chunks": 1,
            "note":   "direct prediction"
        }

    # Long text chunking
    raw_ids     = tokenizer(text, add_special_tokens=False)["input_ids"]
    chunk_probs = []
    stride      = 108

    for start in range(0, len(raw_ids), stride):
        chunk = raw_ids[start:start + 126]
        if not chunk:
            break
        chunk   = [101] + chunk + [102]
        padding = [0] * (128 - len(chunk))
        mask    = [1] * len(chunk) + [0] * len(padding)
        chunk   = chunk + padding

        input_ids      = torch.tensor([chunk]).to(device)
        attention_mask = torch.tensor([mask]).to(device)

        with torch.no_grad():
            logits = model(
                input_ids=input_ids,
                attention_mask=attention_mask
            ).logits
            probs = torch.softmax(logits, dim=-1)[0]
        chunk_probs.append(probs)

        if start + 126 >= len(raw_ids):
            break

    avg   = torch.stack(chunk_probs).mean(dim=0)
    top_id = torch.argmax(avg).item()

    return {
        "emotion":    KAAM_ID2LABEL[top_id],
        "confidence": round(avg[top_id].item(), 4),
        "all_scores": {
            KAAM_ID2LABEL[i]: round(avg[i].item(), 4)
            for i in range(len(KAAM_ID2LABEL))
        },
        "chunks": len(chunk_probs),
        "note":   f"averaged across {len(chunk_probs)} chunks"
    }

# ── Endpoints ────────────────────────────────────────────────
@app.get("/")
def health():
    return {
        "status":   "KAAM Emotion API running ✓",
        "model":    "distilbert-kaam-v1",
        "emotions": list(KAAM_LABEL2ID.keys())
    }

@app.post("/detect-emotion")
def detect_emotion(request: EmotionRequest):
    if not request.text.strip():
        return {"emotion": "neutral", "confidence": 1.0,
                "all_scores": {}, "chunks": 0, "note": "empty"}
    return predict_emotion(request.text)

@app.post("/detect-emotion/batch")
def detect_batch(texts: list[str]):
    return {"results": [predict_emotion(t) for t in texts[:10]]}
