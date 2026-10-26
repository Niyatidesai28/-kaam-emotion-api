# Verification report — 26 October 2026

| Check | Status | Evidence |
|---|---|---|
| Dependency install | PASS | pinned requirements + dev tools installed in isolated Python3.10.21 |
| Normal Uvicorn startup | FAIL; genuine inference BLOCKED | FileNotFoundError for model/kaam_config.json; no artifacts in clone |
| Baseline regression suite | FAIL | 3 failed/10 passed: two blank-input cases and model path |
| Repaired fixture suite | PASS | 13 passed; 13 httpx/Starlette compatibility deprecation warnings |
| Single/health contract | PASS with fixtures | actual FastAPI routes; synthetic labels/logits/tokenizer |
| Chunk boundaries/padding | PASS with fixtures |126,127,234,235,500 synthetic content tokens; shapes[1,128] |
| Softmax/mean output | PASS with fixtures | real torch arithmetic over controlled [0,2] logits ->0.8808 |
| Blank single/batch parity | PASS | both return sentinel without model calls |
| Invalid JSON schema | PASS | missing/null/numeric single text and invalid batch shapes/elements ->422 |
| Batch cap | PASS documenting current behavior |11 input strings yield10 results; not an endorsement of silent truncation |
| Compile/static syntax | PASS | compileall main.py/tests and git diff --check |
| Secret pattern scan | PASS, limited | no matching token/private-key patterns in candidate files |
| Dependency advisories | FAIL |96 scanner records across6 packages; duplicates included, not96 independent proven exploits |
| Real model accuracy/inference | BLOCKED | original weights/tokenizer/config and labeled evaluation data absent |
| Frontend/onboarding/chat E2E | BLOCKED | no corresponding source |
| Database integration | BLOCKED / absent | no database code/configuration |
| GPU/load/calibration/fairness | NOT TESTED | no real model or evaluation dataset |
| Linter/type checker | NOT TESTED | not configured in baseline |

Reproduce from root:
```sh
python3.10 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest tests -q
.venv/bin/python -m compileall -q main.py tests
# Fails until authorized original model files are placed under model/
HF_HUB_OFFLINE=1 .venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8001
```

The fixture patches only config reading and from_pretrained loaders. It creates no pretend
model/ directory and does not turn production startup into a synthetic-success mode. Tests
use actual route validation and PyTorch operations; semantic predictions remain unverified.
No browser screenshot, deployed endpoint or complete KAAM application PASS is claimed.
