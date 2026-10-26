"""API/pipeline tests with synthetic tokenizer/logits; NOT trained-model validation."""
import importlib.util
import io
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
import torch
from fastapi.testclient import TestClient
from transformers import AutoModelForSequenceClassification, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]


class Inputs(dict):
    def to(self, device):
        return Inputs({key: value.to(device) for key, value in self.items()})


class Tokenizer:
    def __call__(self, text, add_special_tokens=True, return_tensors=None, **kwargs):
        ids = [10] * len(text.split())
        if add_special_tokens:
            ids = [101] + ids + [102]
        if return_tensors:
            ids = ids[:128]
            mask = [1] * len(ids) + [0] * (128-len(ids))
            ids += [0] * (128-len(ids))
            return Inputs(input_ids=torch.tensor([ids]), attention_mask=torch.tensor([mask]))
        return {'input_ids': ids}


class Model:
    def __init__(self): self.calls = []
    def to(self, device): return self
    def eval(self): return self
    def __call__(self, **inputs):
        self.calls.append(inputs)
        return SimpleNamespace(logits=torch.tensor([[0., 2.]], device=inputs['input_ids'].device))


@pytest.fixture
def api():
    real_open = open
    def config_open(path, *args, **kwargs):
        if str(path).endswith('kaam_config.json'):
            return io.StringIO(json.dumps({'id2label': {'0': 'neutral', '1': 'happy'}, 'label2id': {'neutral': 0, 'happy': 1}}))
        return real_open(path, *args, **kwargs)
    fake = Model()
    spec = importlib.util.spec_from_file_location('kaam_test_app', ROOT/'main.py')
    module = importlib.util.module_from_spec(spec)
    with patch('builtins.open', config_open), patch.object(AutoTokenizer, 'from_pretrained', return_value=Tokenizer()), patch.object(AutoModelForSequenceClassification, 'from_pretrained', return_value=fake):
        spec.loader.exec_module(module)
    with TestClient(module.app) as client:
        yield module, fake, client


def test_health_and_response_contract(api):
    module, model, client = api
    assert client.get('/').json()['emotions'] == ['neutral', 'happy']
    result = client.post('/detect-emotion', json={'text': 'I feel good'}).json()
    assert result == {'emotion': 'happy', 'confidence': .8808, 'all_scores': {'neutral': .1192, 'happy': .8808}, 'chunks': 1, 'note': 'direct prediction'}
    assert not model.calls[0]['input_ids'].requires_grad


@pytest.mark.parametrize('words,chunks', [(126, 1), (127, 2), (234, 2), (235, 3), (500, 5)])
def test_chunk_boundaries_padding_and_average(api, words, chunks):
    module, model, client = api
    result = module.predict_emotion(' '.join(['word']*words))
    assert result['chunks'] == chunks
    assert result['confidence'] == .8808
    assert len(model.calls) == chunks
    for call in model.calls:
        assert call['input_ids'].shape == (1,128)
        assert call['attention_mask'].shape == (1,128)
        assert call['input_ids'][0,0].item() == 101


@pytest.mark.parametrize('text', ['', '  \n\t '])
def test_empty_inputs_consistent_in_single_and_batch(api, text):
    module, model, client = api
    single = client.post('/detect-emotion', json={'text': text}).json()
    batch = client.post('/detect-emotion/batch', json=[text]).json()['results'][0]
    assert single == batch == {'emotion': 'neutral', 'confidence': 1.0, 'all_scores': {}, 'chunks': 0, 'note': 'empty'}
    assert model.calls == []


@pytest.mark.parametrize('body', [{}, {'text': None}, {'text': 42}])
def test_single_schema_errors(api, body):
    assert api[2].post('/detect-emotion', json=body).status_code == 422


def test_batch_contract_and_existing_limit(api):
    client=api[2]
    assert client.post('/detect-emotion/batch', json=[]).json() == {'results': []}
    assert len(client.post('/detect-emotion/batch', json=['ok']*11).json()['results']) == 10
    assert client.post('/detect-emotion/batch', json={'texts': ['ok']}).status_code == 422
    assert client.post('/detect-emotion/batch', json=[None]).status_code == 422


def test_model_path_is_independent_of_working_directory(api):
    assert Path(api[0].MODEL_PATH).is_absolute()
    assert Path(api[0].MODEL_PATH) == ROOT/'model'
