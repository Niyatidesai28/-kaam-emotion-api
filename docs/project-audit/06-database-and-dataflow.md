# Database and data lifecycle

There is no SQL database, database client, ORM, schema, table, migration, query or transaction.
No input text, user profile, session, conversation or prediction is persisted by this code.
The user_id field has no operational effect. Local model/config files are artifacts,
not relational storage.

```mermaid
flowchart LR
  json["Incoming JSON"] --> request["EmotionRequest or list validation"]
  request --> text["Transient text in memory"]
  text --> tokens["Token ID arrays"]
  tokens --> tensors["CPU/CUDA tensors"]
  tensors --> scores["Per-label probabilities"]
  scores --> output["JSON response"]
```

Token count for N content tokens requires full tokenization. Long text needs approximately
ceil((N-126)/108)+1 windows for N>126. Each window has a fixed 128-token input shape, but
classifier cost depends on its actual architecture. Runtime grows with windows; concurrent
requests add pressure. Request parsing is not capped by slicing a list after it is received.
The absence of storage reduces some retention risk but does not imply network privacy:
there is no authentication, rate limiting or deployment TLS configuration here.

Optional extension only: a prediction table could record id, user_id, model_version and
scores, with explicit retention/consent choices. Storing raw personal text is a separate
product/privacy decision. Do not add it merely to justify the resume's SQL claim.
