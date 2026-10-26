# Complete source inventory

| Original file | Role |
|---|---|
| main.py:2–26 | imports, label JSON, tokenizer/model loading, CUDA-or-CPU selection, evaluation mode |
| main.py:29–36 | FastAPI app and wildcard-origin CORS |
| main.py:39–41 | EmotionRequest with required text and optional user_id='anon' |
| main.py:44–113 | predict_emotion: token count, direct path or overlapped chunks, softmax/average/argmax |
| main.py:116–133 | health, single and batch endpoints |
| requirements.txt | six pinned direct dependencies |
| runtime.txt | declared python-3.10.0 runtime |
| Procfile | Uvicorn process using host-supplied PORT |
| .gitignore | excludes model/, binary weights, .env, Python cache; audit adds .venv/test cache |

Audit additions: requirements-dev.txt, tests/test_api.py, docs/project-audit.
See SOURCE-INDEX.md. There are no source subdirectories or generated vendor files to map.
`os` was unused and the audit uses pathlib.Path for stable model resolution. NumPy is not
called by application code. KAAM_LABEL2ID is used only to expose labels in health; user_id
is dead input. No README, CI, Dockerfile, migrations, React components or training script
was present. Line references above are baseline references; small repairs shift later lines.
