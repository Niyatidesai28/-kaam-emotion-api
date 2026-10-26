# API contract and tested scope

Normal startup requires the missing model artifacts. The following contracts are verified
with the application's actual routes and synthetic classifier/tokenizer fixtures.

| Method / route | Request | Handler / logic | Response | Errors |
|---|---|---|---|---|
| GET / | none | health | 200 status, model name string, label names | unavailable if import fails |
| POST /detect-emotion | {text: string, user_id?: string} | detect_emotion -> predict_emotion | 200 prediction or blank sentinel | 422 missing/null/non-string text; unhandled inference errors -> 500 |
| POST /detect-emotion/batch | JSON array of strings | detect_batch -> predict_emotion for first ten | 200 {results: prediction[]} | 422 object/null elements; inference exception aborts whole batch |

No query/path parameters, auth, service-layer network calls or database operations.
Prediction fields: emotion string, confidence number rounded to four decimals, all_scores
label -> score map, chunks integer, note string. Actual label names depend on missing config.
The fixture uses neutral/happy only; those are not claims about the real classifier's taxonomy.

Single example: {"text":"I feel ready to try again","user_id":"demo"}.
Batch example: ["first message","second message"], not {"texts":[...]}.
Blank input yields neutral, confidence=1.0, empty scores, chunks=0, note='empty'; that value
is a sentinel rather than model certainty. The audit makes batch use the same behavior.
An empty batch returns an empty results list. Eleven texts still return ten results,
preserving the existing contract while documenting silent truncation as a defect to redesign.

CORS allows all origins and methods/headers; credentials are not enabled. Generated docs
and OpenAPI exist only after successful application import. No frontend integration was tested.
