import os

import requests
from flask import Flask, jsonify, render_template, request

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL = os.getenv("OLLAMA_MODEL", "llama3")

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/query", methods=["POST"])
def query_ollama():
    prompt = (request.get_json(silent=True) or {}).get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "Please type a prompt."}), 400

    try:
        reply = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=120,
        )
        reply.raise_for_status()
    except requests.RequestException:
        return jsonify({"error": "Couldn't reach Ollama. Is it running?"}), 502

    return jsonify({"response": reply.json().get("response", "")})


if __name__ == "__main__":
    # Debug mode is for your own machine only. Never turn it on for a public link.
    debug = os.getenv("FLASK_DEBUG") == "1"
    app.run(host=os.getenv("HOST", "127.0.0.1"), port=5000, debug=debug)
