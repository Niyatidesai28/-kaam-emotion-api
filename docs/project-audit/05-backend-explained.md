# Backend implementation, step by step

At import, main.py opens model/kaam_config.json, converts id2label JSON keys to integers,
loads a tokenizer and sequence classifier from the same directory, chooses CUDA when
available (otherwise CPU), moves the model and calls eval(). The audit makes the directory
relative to main.py rather than the shell's working directory. Files are still required.

EmotionRequest is a Pydantic schema. text must be a string; user_id defaults to anon but
is ignored after parsing. There is no session, authentication or chat message model.

predict_emotion first handles blank text (audit unifies this rule for both routes). For
nonblank text it tokenizes without truncation to count input length. At <=128 tokens it
encodes again with max-length padding/truncation, moves tensors to the selected device,
and calls the model with torch.no_grad. Logits are raw scores; softmax produces normalized
relative scores; argmax selects a label. Values are rounded to four decimals.

For long input, it tokenizes without special tokens. Windows contain up to 126 content
tokens, advancing 108 tokens each time: full adjacent windows overlap 18 tokens. It adds
hardcoded 101/102 special IDs, pads with 0 to 128 and builds an attention mask. Each window
is scored separately. torch.stack(...).mean(dim=0) gives equal weight to each window,
including a short tail. It stops when a window covers the last token, avoiding an extra
redundant tail. Final argmax/confidence come from the mean, not mean logits.

Routes are synchronous def handlers, so FastAPI uses worker threads. No application-level
inference queue, GPU concurrency control, time limit or request-size bound exists. Batch
is sequential and slices to the first ten texts silently. An uncaught model/label error
becomes a server error; no special fallback is implemented. The neutral blank response
is a deterministic sentinel, not a model prediction or calibrated 100% confidence.

Training, loss functions, optimizer, checkpoints, metrics and bias evaluation are absent.
Health's DistilBERT name is a string, not independent architecture evidence. Tests exercise
real tensor arithmetic but replace the tokenizer and classifier with synthetic fixtures.
