# Ollama Flask Web App

A private AI chat app you run yourself. [Ollama](https://ollama.com) runs the language model on your own machine or server, a small Flask app streams its answers, and a plain HTML page gives you a clean chat window. Nothing goes to an outside AI service.

Full guide: [Build Your Own AI-Powered Web App with Ollama and Flask](https://jeremyanderson.tech/build-your-own-ai-powered-web-app-with-ollama-flask/)

## Features

- **Streaming answers**: text appears as the model writes it, with a Stop button
- **Real conversations**: the model sees earlier messages in the chat
- **Model picker**: lists every model you've installed in Ollama
- **Light and dark themes**, keyboard friendly (Enter sends, Shift+Enter adds a line), works offline
- **Clear errors** when Ollama isn't running or a model isn't installed
- **Production-ready Docker image** with Gunicorn, running as a non-root user
- **Tests** with pytest, run on every pull request

## Run it locally

1. Install [Ollama](https://ollama.com) and pull a model:

   ```bash
   ollama pull llama3
   ```

2. Get the code and install the requirements:

   ```bash
   git clone https://github.com/CptNope/Ollama-Flask-Web-App
   cd Ollama-Flask-Web-App
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Start the app and open <http://localhost:5000>:

   ```bash
   python app.py
   ```

## Settings

All settings are environment variables:

| Variable | Default | What it does |
|---|---|---|
| `OLLAMA_URL` | `http://localhost:11434` | Where Ollama is running |
| `OLLAMA_MODEL` | `llama3` | Model selected when the page opens |
| `SYSTEM_PROMPT` | (none) | Instructions added to every conversation |
| `HOST` / `PORT` | `127.0.0.1` / `5000` | Address for `python app.py` |
| `FLASK_DEBUG` | off | Set to `1` for Flask's debugger. **Never on a public address.** |

Example: `OLLAMA_MODEL=mistral SYSTEM_PROMPT="Answer briefly." python app.py`

## Share it with Cloudflare Tunnel

A quick tunnel gives your local app an HTTPS link without opening ports, and needs no Cloudflare account:

```bash
cloudflared tunnel --url http://localhost:5000
```

Before you share the link:

- **Keep debug mode off.** Flask's debugger lets anyone who can open the page run Python code on your machine.
- **Anyone with the link can use your model**, and your hardware does the work. For more than a quick demo, use a named tunnel on your own domain with [Cloudflare Access](https://developers.cloudflare.com/cloudflare-one/) in front, so only people you allow can sign in.
- **Quick tunnels are for testing**: no uptime guarantee, and a new address each time.

## Deploy with Docker

Install Ollama on the server (larger models need a GPU) and pull your model, then:

```bash
docker build -t ollama-flask-app .
docker run -d -p 5000:5000 \
  --add-host=host.docker.internal:host-gateway \
  -e OLLAMA_MODEL=llama3 \
  ollama-flask-app
```

The image runs Gunicorn on port 5000 and reaches Ollama on the host at `host.docker.internal:11434`. Put Caddy or Nginx in front for HTTPS, and add a login (Cloudflare Access, or your proxy's authentication) before it's public.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Ideas for what's next

- Retrieval-augmented generation (RAG) over your own documents with a vector database
- Voice in and out with Whisper and a text-to-speech engine such as Piper
- Image generation with Stable Diffusion or ComfyUI alongside Ollama
- User accounts and saved chats
- Install it as a progressive web app

## Project layout

```
app.py              Flask app: page, /api/models, /api/chat (streaming)
templates/index.html
static/style.css
static/script.js
tests/test_app.py
Dockerfile
requirements.txt
requirements-dev.txt
```

## Author

Created by [Jeremy Anderson](https://jeremyanderson.tech), MIT licensed.
