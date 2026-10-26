# Practical KAAM exercises

1. Build a label-map validator. Require IDs 0..N-1 and a reverse map consistent with them;
   fail with a useful error for gaps. No real label taxonomy may be guessed.
2. Write a chunker with width126/stride108. For235 IDs expect lengths126,126,19; verify
   coverage, overlap18 and no empty chunks. Explain why a234-ID input needs only two.
3. Produce padded IDs and masks for five content IDs plus two specials. Assert length128,
   seven ones followed by121 zeros. Then parameterize the special IDs for an authorized tokenizer.
4. Given probability vectors [0.2,0.8] and [0.6,0.4], calculate mean [0.4,0.6]. Explain why
   this is not the same operation as averaging arbitrary logits and applying softmax later.
5. Reproduce single/batch whitespace inconsistency, then centralize the blank policy. The
   final fixture should assert zero model calls and identical response shapes.
6. Propose a documented batch limit policy: reject >10 with422 or process all under a budget.
   Write contract tests and a migration note before changing current silent truncation.
7. Add a maximum text-length validator in a separate practice branch. Include tests showing
   it applies before tokenization and also covers each batch element; choose limits explicitly.
8. Draft an evaluation table with true label, predicted label, confidence and model version.
   Compute per-class precision/recall on a synthetic labeled example and explain why this
   toy exercise is not evidence of the missing real model's performance.

Read tests/test_api.py for test-double structure. The real project uses functions and external
library classes; do not invent a complex OOP hierarchy just to mention interview terminology.
