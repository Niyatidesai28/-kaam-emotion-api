# KAAM interview preparation

## 30-second explanation

“KAAM’s available repository is an emotion-classification backend. FastAPI accepts text and uses a local Transformers/PyTorch classifier. Short text uses one prediction; long text uses overlapping windows and averages scores. The model artifacts and companion frontend are not in the repository, so genuine inference and the full coaching workflow remain unverified.”

## 60-second explanation

Add: “The API offers single and batch endpoints with Pydantic type validation. The code separates tokenization, logits, softmax and label mapping inside one prediction helper. The audit tested chunk boundaries using synthetic outputs and repaired inconsistent blank handling plus working-directory-dependent model loading. There is no SQL, session storage or response-generating chatbot here.”

## Three-minute walkthrough

Use 30 seconds for scope, 40 for import/artifact loading, 60 for short vs chunked inference, 30 for API validation/tests, and 20 for limitations. Walk through main.py rather than describing an imagined frontend. Explain that no_grad is not eval, confidence is not accuracy, and test doubles do not validate an unseen model. Discuss single-module simplicity versus a future loader/service/route separation only when complexity justifies it.

## 1. Is this the complete KAAM app?

No. The five-file baseline is an emotion API. There is no React frontend, onboarding, chat response generation, conversation history or database. A larger product may exist elsewhere, but this repository cannot verify it.

## 2. What is the input/output contract?

Single input is a JSON object with text and optional user_id; output contains emotion, confidence, all_scores, chunks and note. Batch input is a raw string array. Actual emotion labels come from the missing config, not a hardcoded taxonomy.

## 3. What happens before the server starts?

Import opens kaam_config.json, loads AutoTokenizer and AutoModelForSequenceClassification, chooses CPU/CUDA and calls eval. Missing artifacts raise before the FastAPI app is available. This is why the health route cannot diagnose this startup failure.

## 4. What ML is actually implemented?

Source calls a Transformers sequence classifier through PyTorch and applies softmax to logits. That is an inference integration. We cannot verify trained weights, accuracy, dataset or the stated DistilBERT identity because model/ is absent.

## 5. Does the code train a model?

No. There is no optimizer, loss computation, backward pass, dataset split or training loop. from_pretrained loads existing artifacts; the method name does not prove the owner fine-tuned them.

## 6. What is a tokenizer?

It maps text into model vocabulary IDs, often at subword granularity. The audit fixture counts whitespace-separated words only to test control flow; it is not evidence of the real tokenizer behavior.

## 7. Why count tokens first?

The code chooses one padded prediction when total length including special tokens is <=128, otherwise overlapping chunks. This avoids silently truncating long input to its first 128 tokens, at the cost of extra tokenization work.

## 8. What are padding and attention masks?

Padding fills inputs to 128 positions; the mask marks real positions as 1 and padding as 0. The long branch builds both manually. Wrong masks could make padding affect predictions.

## 9. What is the 126/108 relationship?

Each long window holds 126 content tokens plus two special tokens. Starts advance by 108, so adjacent full windows overlap 18 content tokens. The final break stops when a window covers the end.

## 10. How many chunks does 235 content tokens produce?

Starts are 0,108,216; windows cover up to 126 tokens each. The second ends at 234, so one final short window is needed: three calls. The regression suite checks this boundary and 234 yielding two.

## 11. Why are hardcoded IDs risky?

101,102 and 0 assume BERT-style special/pad IDs. AutoTokenizer can load other vocabularies, so these constants are only valid if the actual saved tokenizer agrees. Artifacts are missing, so the audit documents rather than guesses a replacement.

## 12. What are logits?

They are unnormalized label scores returned by model(...).logits. Their absolute values are not probabilities. softmax exponentiates and normalizes them across the label dimension.

## 13. How are long-input predictions combined?

The code takes softmax for each chunk, stacks those probability vectors and averages them equally. It then takes argmax. Averaging probabilities differs from averaging logits, and overlap means some tokens influence more than one chunk.

## 14. Is confidence calibrated certainty?

No. It is the largest softmax or mean-softmax score rounded to four decimals. Calibration requires comparing scores against labeled held-out outcomes. The blank-input 1.0 is only an explicit sentinel and does not come from ML.

## 15. What does model.eval do?

It changes training-sensitive module behavior, such as disabling dropout. It does not disable automatic gradient tracking. The separate torch.no_grad context avoids retaining gradient history during inference.

## 16. Why use torch.no_grad?

Training gradients are unnecessary when serving predictions. Disabling recording reduces memory/work. Model parameters are not updated anywhere in this application.

## 17. Which device is selected?

CUDA if torch.cuda.is_available, otherwise CPU. It does not select Apple MPS. The tests ran on CPU. GPU performance and concurrency were not verified.

## 18. How are labels mapped?

JSON id2label keys are strings; the loader converts them to integers for tensor-index lookup. The reverse map is used in health. There is no consistency check that label count matches model output size.

## 19. What validation exists?

Pydantic validates required string text and string user_id, while the prediction helper handles blank text. Missing, null and numeric text produce 422. There is no character/token upper bound and user_id is not authorization.

## 20. What was the empty batch bug?

The single route bypassed inference for whitespace, but batch called predict_emotion directly and returned a classifier result. Moving the existing empty rule into the shared helper gives both routes identical behavior without duplicating logic.

## 21. What does batch mean here?

The endpoint loops sequentially over texts[:10]. It is not tensor batching for GPU efficiency, and it silently drops later entries. A revised API should choose explicit rejection/pagination semantics with consumers before changing that behavior.

## 22. Where are users and sessions stored?

Nowhere. user_id defaults to anon and is ignored. The code neither authenticates it nor links it to stored records. Do not infer sessions from the field name.

## 23. How would you describe the database design?

There is no database to describe. Model files are not SQL tables. A future prediction-history schema needs ownership and retention decisions, especially because submitted text may contain personal information.

## 24. Does wildcard CORS imply public access security?

No. Any browser origin can call/read under this configuration, and there is no authentication. CORS is not a request authorization mechanism; direct clients are not secured by it either.

## 25. What happens on inference failure?

There is no try/except around model calls or label lookups. FastAPI returns a server error; in a batch, one failure aborts the full response. A useful improvement is structured failure handling without logging raw sensitive text.

## 26. How would you debug the current startup?

Read the first application frame in the traceback: open of model/kaam_config.json fails. Confirm the model directory and exact filenames, then compatible tokenizer/weights. Installing dependencies alone cannot supply the private/custom trained model.

## 27. What does the path fix accomplish?

Path(__file__).resolve().parent / model anchors files to the module location instead of the current shell directory. It makes launches reproducible from another folder but does not repair missing artifacts.

## 28. What do the 13 tests prove?

They verify real route parsing, response shape, softmax arithmetic with synthetic logits, chunk boundary/padding shapes, blank parity, schema errors and current batch cap. They do not verify trained semantic predictions, real tokenizer IDs or complete product integration.

## 29. How would you evaluate a real model?

Obtain authorized versioned weights/tokenizer and a representative labeled holdout set; measure per-class precision/recall/F1, confusion matrix and calibration. Include short/long text, languages and sensitive subgroups with appropriate consent. No such measurement exists here.

## 30. What are the performance risks?

Unbounded request text is fully tokenized; long requests trigger many sequential model calls. Multiple threadpool requests may compete for CPU/GPU memory. Add measured limits/queueing and load tests after choosing a service budget.

## 31. How does this help with SAP interviews?

It shows typed API contracts, boundary handling, transformations and debugging missing dependencies/artifacts. These transfer to backend business logic and enterprise integration. It does not demonstrate ABAP, MM configuration or GRC implementation.

## 32. How should the resume describe this repository?

Describe a FastAPI emotion-classification backend with Transformer/PyTorch integration and overlapping-window aggregation. Qualify missing artifacts and frontend. Do not claim full onboarding/chat, SQL, training accuracy or production deployment based on this code alone.
