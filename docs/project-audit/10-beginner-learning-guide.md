# Learn the actual emotion service

## 1. Python objects, dictionaries and JSON

A Python dict maps keys to values. JSON object keys arrive as strings. main.py converts
id2label keys using `{int(k): v for k,v in config['id2label'].items()}` so numeric argmax
indices can find labels. Independent example:
```python
labels = {int(k): v for k,v in {'0':'calm','1':'upset'}.items()}
assert labels[1] == 'upset'
```
Exercise: validate contiguous IDs and reject duplicate reverse-map labels. Common mistake:
accessing labels[1] when the actual key is '1'. This configuration is missing in the clone.

## 2. HTTP and Pydantic

A POST sends data for processing. FastAPI decorators bind functions to routes; BaseModel
fields define the body contract. `text: str` is required; `user_id: str='anon'` has a default.
These are request fields, not SQL columns. Example:
```python
from pydantic import BaseModel
class Message(BaseModel):
    text: str
assert Message(text='hello').text == 'hello'
```
Exercise: send missing/null/numeric text and inspect 422. Common mistake: posting an object
to the batch route, which expects an array. A synchronous route can use a threadpool; it
does not make CPU/GPU work free or safely bounded.

## 3. Tokenization, sequences and tensors

A tokenizer maps text to integer vocabulary IDs; tokens may be word pieces. Lists are
ordinary Python collections; tensors are numeric arrays used by the model. Batch and
sequence dimensions here are [1,128]. Example:
```python
import torch
ids = torch.tensor([[101, 10, 102, 0]])
mask = torch.tensor([[1, 1, 1, 0]])
assert ids.shape == mask.shape == (1,4)
```
Exercise: pad a three-token sequence to length eight and build its mask. Do not assume
these IDs work for every tokenizer; the real artifact must define its vocabulary.

## 4. Inference and probabilities

A trained classifier maps input tensors to logits. `torch.softmax(logits,dim=-1)` normalizes
across labels. `argmax` picks the largest index. Example with synthetic values:
```python
p = torch.softmax(torch.tensor([0.,2.]), dim=-1)
assert round(p[1].item(),4) == .8808
```
Exercise: explain why adding the same constant to both logits preserves probabilities.
The model itself is not trained by this code. eval disables training behavior; no_grad
avoids recording gradients. Neither proves correctness. Hugging Face Auto classes select
implementations using artifact configuration; the health string alone proves no architecture.

## 5. Sliding windows and aggregation

main.py slices raw_ids[start:start+126] and advances start by 108. Python's slice end is
exclusive. The resulting overlap preserves some context at boundaries, but repeated tokens
and short tails influence equal-weight averaging. Example:
```python
ids = list(range(235))
windows=[]
for start in range(0,len(ids),108):
    windows.append(ids[start:start+126])
    if start+126 >= len(ids): break
assert list(map(len,windows)) == [126,126,19]
```
Exercise: prove 234 tokens creates only two windows. Common mistake: processing an extra
redundant tail or describing an arithmetic mean as a trained ranking model.

## 6. Artifacts, runtime and reproducibility

requirements.txt pins direct libraries; runtime.txt requests Python 3.10.0. The audit used
compatible managed Python 3.10.21. Procfile asks the host to supply PORT; it does not provision
a model. model/ is ignored intentionally, so source recovery does not recover weights.
Exercise: inventory authorized artifacts, versions and hashes without publishing personal
training data. Use pathlib to anchor paths. Never download arbitrary pickle weights merely
to make startup green. NumPy is declared but not directly called by main.py.

## 7. Testing and honest evidence

Read tests/test_api.py: TestClient runs real routes; fake tokenizer/model supply controlled
values; PyTorch performs real tensor math. Patches are scoped to each fixture, so no model
files are generated. Exercise: reintroduce the old blank check location and observe two
regressions. Compare this with real integration testing, which requires actual artifacts.
Errors should lead to reproducible tests, not a fabricated healthy service.
