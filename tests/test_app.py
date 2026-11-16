import json

import pytest
import requests

import app as webapp


class FakeResponse:
    def __init__(self, status=200, body=None, lines=None):
        self.status_code = status
        self._body = body or {}
        self._lines = lines or []
        self.closed = False

    def json(self):
        return self._body

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(str(self.status_code))

    def iter_lines(self):
        for line in self._lines:
            yield json.dumps(line).encode()

    def close(self):
        self.closed = True


@pytest.fixture
def client():
    webapp.app.config["TESTING"] = True
    return webapp.app.test_client()


def test_index_renders(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"Ask your own AI anything." in res.data


def test_models_lists_installed_models(client, monkeypatch):
    monkeypatch.setattr(webapp.requests, "get", lambda *a, **k: FakeResponse(body={"models": [{"name": "mistral:latest"}, {"name": "llama3:latest"}]}))
    res = client.get("/api/models")
    assert res.get_json() == {"models": ["llama3:latest", "mistral:latest"], "default": webapp.DEFAULT_MODEL}


def test_models_reports_ollama_down(client, monkeypatch):
    def down(*a, **k):
        raise requests.ConnectionError()

    monkeypatch.setattr(webapp.requests, "get", down)
    res = client.get("/api/models")
    assert res.status_code == 502
    assert "ollama serve" in res.get_json()["error"]


def test_chat_streams_answer(client, monkeypatch):
    sent = {}

    def fake_post(url, json=None, **kwargs):
        sent.update(url=url, body=json, kwargs=kwargs)
        return FakeResponse(lines=[
            {"message": {"role": "assistant", "content": "Hello"}, "done": False},
            {"message": {"role": "assistant", "content": " there"}, "done": False},
            {"message": {"role": "assistant", "content": ""}, "done": True},
        ])

    monkeypatch.setattr(webapp.requests, "post", fake_post)
    res = client.post("/api/chat", json={"model": "llama3", "messages": [{"role": "user", "content": "Hi"}]})
    assert res.status_code == 200
    assert res.get_data(as_text=True) == "Hello there"
    assert sent["url"].endswith("/api/chat")
    assert sent["body"]["stream"] is True
    assert sent["kwargs"]["stream"] is True


def test_chat_rejects_bad_input(client):
    assert client.post("/api/chat", json={"messages": []}).status_code == 400
    assert client.post("/api/chat", json={"messages": [{"role": "system", "content": "x"}]}).status_code == 400
    assert client.post("/api/chat", json={"messages": [{"role": "user", "content": "x" * 20001}]}).status_code == 400
    assert client.post("/api/chat", json={"model": "bad model;rm", "messages": [{"role": "user", "content": "hi"}]}).status_code == 400


def test_chat_missing_model_says_how_to_install(client, monkeypatch):
    monkeypatch.setattr(webapp.requests, "post", lambda *a, **k: FakeResponse(status=404, body={"error": "model not found"}))
    res = client.post("/api/chat", json={"model": "phi3", "messages": [{"role": "user", "content": "hi"}]})
    assert res.status_code == 502
    assert "ollama pull phi3" in res.get_json()["error"]


def test_chat_ollama_down(client, monkeypatch):
    def down(*a, **k):
        raise requests.ConnectionError()

    monkeypatch.setattr(webapp.requests, "post", down)
    res = client.post("/api/chat", json={"messages": [{"role": "user", "content": "hi"}]})
    assert res.status_code == 502


def test_old_generate_url_setting_still_works(monkeypatch):
    import importlib

    monkeypatch.setenv("OLLAMA_URL", "http://box:11434/api/generate")
    reloaded = importlib.reload(webapp)
    assert reloaded.OLLAMA_URL == "http://box:11434"
    monkeypatch.delenv("OLLAMA_URL")
    importlib.reload(webapp)
