# Architecture: inference service only

```mermaid
flowchart LR
  client["External client; frontend absent"] --> api["FastAPI routes in main.py"]
  files["Local model and label artifacts - absent"] --> tokenizer["AutoTokenizer"]
  files --> model["AutoModelForSequenceClassification"]
  api --> predict["predict_emotion"]
  predict --> tokenizer
  tokenizer --> windows["128-token padded inputs"]
  windows --> model
  model --> softmax["Softmax per chunk"]
  softmax --> average["Mean if multiple chunks"]
  average --> response["Argmax label + scores"]
  response --> client
```

```mermaid
flowchart TD
  request["Single request object or batch list"] --> schema["Pydantic validation"]
  schema -->|"Invalid"| error["422 response"]
  schema -->|"Valid"| blank["Whitespace-only text?"]
  blank -->|"Yes"| neutral["Neutral sentinel, no inference"]
  blank -->|"No"| count["Tokenize and count"]
  count -->|"At most 128 including specials"| direct["One padded model call"]
  count -->|"More than 128"| chunks["126 content tokens, stride 108"]
  chunks --> mean["Mean probabilities"]
  direct --> label["Top label and rounded confidence"]
  mean --> label
```

```mermaid
sequenceDiagram
  participant C as API client
  participant A as FastAPI
  participant T as Tokenizer
  participant M as Classifier
  C->>A: POST detect-emotion
  A->>A: Validate text and check blank
  A->>T: Count tokens
  A->>T: Encode padded input or chunks
  A->>M: Tensor inference under no_grad
  M-->>A: Logits
  A->>A: Softmax, mean, argmax, labels
  A-->>C: JSON result
```

```mermaid
flowchart LR
  start["Import main.py"] --> config["Open kaam_config.json"]
  config -->|"Missing"| fail["Startup error; app unavailable"]
  config -->|"Present"| weights["Load local tokenizer/weights"]
  weights --> device["CUDA if available, else CPU"]
  device --> eval["model.eval"]
  eval --> serve["Uvicorn serves routes"]
```

No frontend component hierarchy, database ER diagram, authentication flow or chat journey
can be truthfully drawn from this repository. Its data flow is transient text -> tokens ->
tensors -> scores -> response; there is no storage edge. Model loading occurs at import,
not a FastAPI lifespan hook, so missing files prevent even the health endpoint from starting.
