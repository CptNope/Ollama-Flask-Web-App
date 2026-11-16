"""Ollama Flask Web App: a private AI chat app that runs on your own machine.

Ollama runs the model, this Flask app streams its answers to a small web page.
Settings come from environment variables (see README.md).
"""

import json
import os
import re

import requests
from flask import Flask, Response, jsonify, render_template, request, stream_with_context

# Base address of Ollama. An older setting that pointed at /api/generate still works.
OLLAMA_URL = re.sub(r"/api/generate/?$", "", os.getenv("OLLAMA_URL", "http://localhost:11434")).rstrip("/")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "").strip()

MAX_MESSAGES = 50  # turns sent back to the model
MAX_CHARS = 20000  # total characters in one request
MODEL_NAME = re.compile(r"^[\w.:/-]{1,100}$")

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", default_model=DEFAULT_MODEL)


@app.get("/api/models")
def models():
    """Models installed in Ollama, so the page can offer a choice."""
    try:
        reply = requests.get(f"{OLLAMA_URL}/api/tags", timeout=10)
        reply.raise_for_status()
    except requests.RequestException:
        return jsonify({"error": "Can't reach Ollama. Start it with `ollama serve`."}), 502
    names = sorted(m.get("name", "") for m in reply.json().get("models", []) if m.get("name"))
    return jsonify({"models": names, "default": DEFAULT_MODEL})


def clean_messages(raw):
    """Keep only well-formed user/assistant turns, within the size limits."""
    if not isinstance(raw, list):
        return None
    messages = []
    for item in raw[-MAX_MESSAGES:]:
        if not isinstance(item, dict):
            return None
        role, content = item.get("role"), item.get("content")
        if role not in ("user", "assistant") or not isinstance(content, str):
            return None
        messages.append({"role": role, "content": content})
    if not messages or messages[-1]["role"] != "user" or not messages[-1]["content"].strip():
        return None
    if sum(len(m["content"]) for m in messages) > MAX_CHARS:
        return None
    return messages


@app.post("/api/chat")
def chat():
    """Send the conversation to Ollama and stream the answer back as plain text."""
    body = request.get_json(silent=True) or {}
    messages = clean_messages(body.get("messages"))
    if messages is None:
        return jsonify({"error": "Type a message first (up to 20,000 characters in a conversation)."}), 400

    model = body.get("model") or DEFAULT_MODEL
    if not isinstance(model, str) or not MODEL_NAME.match(model):
        return jsonify({"error": "That model name isn't valid."}), 400

    if SYSTEM_PROMPT:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    try:
        upstream = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={"model": model, "messages": messages, "stream": True},
            stream=True,
            timeout=(5, 300),
        )
    except requests.RequestException:
        return jsonify({"error": "Can't reach Ollama. Start it with `ollama serve`."}), 502

    if upstream.status_code != 200:
        try:
            detail = upstream.json().get("error", "")
        except ValueError:
            detail = ""
        upstream.close()
        if upstream.status_code == 404:
            detail = f"Model {model} isn't installed. Run `ollama pull {model}`."
        return jsonify({"error": detail or "Ollama returned an error."}), 502

    def generate():
        try:
            for line in upstream.iter_lines():
                if not line:
                    continue
                chunk = json.loads(line)
                if chunk.get("error"):
                    yield f"\n\n[Ollama error: {chunk['error']}]"
                    return
                yield chunk.get("message", {}).get("content", "")
                if chunk.get("done"):
                    return
        except (requests.RequestException, ValueError):
            yield "\n\n[The connection to Ollama was lost.]"
        finally:
            upstream.close()

    return Response(
        stream_with_context(generate()),
        mimetype="text/plain; charset=utf-8",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    # Debug mode is for your own machine only. Never turn it on for a public link:
    # Flask's debugger lets anyone who can open the page run Python code.
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG") == "1",
    )
