# KAAM: actual project specification

This repository is an emotion-classification API, apparently intended to support a larger
KAAM / Comeback Coach application. It accepts text and returns a predicted label, confidence,
all label scores, number of processed chunks and an explanatory note. No coaching response,
conversation, onboarding screen or user profile is implemented here.

Actual stack: Python, FastAPI, Pydantic, Uvicorn, Hugging Face Transformers, PyTorch and NumPy
(dependency). Five original files, one application module. A local classifier/tokenizer must
exist under model/, which is ignored and absent. The health string calls the model
'distilbert-kaam-v1'; architecture, weights, provenance and label set cannot be independently
verified without artifacts. Source contains real ML inference calls, not rule-based emotion
classification, but real inference is BLOCKED in the available checkout.

Implemented paths: single-text prediction, batch request capped to first ten entries,
short-input padded prediction, long-input overlapping windows averaged at probability level,
and a deterministic neutral response for blank input. Audit tests use synthetic logits and
a tokenizer double. They verify orchestration, not learned semantic accuracy.

Target user of this repository is an application client calling the API. Intended end-user
coaching journeys belong to missing software and cannot be reconstructed from this code.
No frontend, SQL, auth, durable user state, training, evaluation dataset or deployment
verification exists. user_id is accepted but never consumed. Do not equate it with a session.
