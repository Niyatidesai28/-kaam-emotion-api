# Rebuild a simplified emotion API

Prerequisites: Python 3.10, virtualenv, HTTP client and basic Python lists/dicts. Work in a
new practice folder. The original model is unavailable; separate a clearly labeled synthetic
learning stage from a real integration stage.

1. Create main.py, requirements.txt, tests/ and model/ (artifact placeholder, ignored).
   Install FastAPI/Uvicorn/Pydantic and add a simple health route. Learn request/response.
2. Add EmotionRequest and POST /detect-emotion with a named classifier dependency. During
   the teaching stage return explicit synthetic scores, never label them genuine ML.
3. Extract a shared empty-input helper so single and batch requests use the same policy.
   Write parity tests plus missing-field/null/type failures. Learn boundary normalization.
4. Implement window slicing independently on integer lists. Test 126,127,234,235 and500
   content-token cases. Then add padding and masks. Learn indexing and off-by-one reasoning.
5. With PyTorch, use synthetic logits to verify softmax, stack/mean and argmax. Assert shapes,
   score keys and rounding. Learn inference post-processing without claiming trained accuracy.
6. Real stage (BLOCKED until artifacts are supplied): obtain the authorized original tokenizer,
   model weights/config and kaam_config.json. Anchor paths to __file__, validate label IDs and
   use AutoTokenizer/AutoModelForSequenceClassification. Do not invent labels or weights.
7. Use eval and no_grad, move inputs/model to the same device, then run known labeled examples.
   Measure quality on a held-out set, not the examples used to develop the model.
8. Integrate a small HTTP client. No frontend or SQL is required to reconstruct this repository.
   Optional history storage is a separate design with consent, ownership and retention.

Minimal first stage:
```python
from fastapi import FastAPI
from pydantic import BaseModel
app=FastAPI()
class EmotionRequest(BaseModel):
    text: str
@app.get('/')
def health(): return {'status':'learning skeleton; no classifier loaded'}
```
Run `uvicorn main:app --host 127.0.0.1 --port 8001`, then inspect /docs. At the real stage,
compare your code with audited main.py. A normal request should traverse validation ->
tokenization -> model -> post-processing -> JSON; no database operation occurs.

Common errors: missing model files -> obtain/version the artifacts; wrong CWD -> use __file__;
shape mismatch -> inspect [batch,sequence] tensors; label mismatch -> compare model output
count to config; wrong batch body -> send raw array; long latency -> inspect token count and
window count. Deployment is not validated by a Procfile alone. Do not expose this unbounded,
unauthenticated service publicly as part of the tutorial.
