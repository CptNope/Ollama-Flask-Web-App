from flask import Flask, request, jsonify, render_template
import requests
import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL = os.getenv("OLLAMA_MODEL", "llama3")

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/query", methods=["POST"])
def query_ollama():
    user_input = request.json.get("prompt")
    response = requests.post(OLLAMA_URL, json={"model": MODEL, "prompt": user_input})
    return jsonify(response.json())

if __name__ == "__main__":
    app.run(debug=True)