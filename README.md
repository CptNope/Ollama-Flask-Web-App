# 🧠 Ollama Flask Web App

A self-hosted, privacy-first language model web app using [Ollama](https://ollama.com), Flask, and optional tunneling with Cloudflare. Perfect for local development, labs, or scaling up to cloud deployment.

---

## 🔧 Project Overview

- **Backend**: Flask (Python)
- **Frontend**: HTML + JavaScript
- **Model API**: Ollama (running locally)
- **Tunnel**: Optional Cloudflare Tunnel for HTTPS access without opening ports
- **Cloud-ready**: Dockerfile included for quick migration

---

## ⚙️ Getting Started Locally

### 1. Clone and Set Up Environment

```bash
git clone https://github.com/CptNope/Ollama-Flask-Web-App
cd ollama-flask-app
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start Ollama

Install [Ollama](https://ollama.com) and run a model:

```bash
ollama run llama3
```

Ensure it's running at: `http://localhost:11434`

### 3. Run Flask App

```bash
python app.py
```

Now open [http://localhost:5000](http://localhost:5000) in your browser.

---

## 🌐 Public Access with Cloudflare Tunnel

To securely access your app without port forwarding:

1. [Install cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/)
2. Authenticate:
```bash
cloudflared tunnel login
```
3. Tunnel your app:
```bash
cloudflared tunnel --url http://localhost:5000
```

You’ll get a public HTTPS link like:
```
https://your-tunnel-id.trycloudflare.com
```

---

## 🐳 Deploy to the Cloud with Docker

To deploy this setup on any cloud VM (AWS, DO, Linode, etc.):

```bash
docker build -t ollama-flask-app .
docker run -p 5000:5000 ollama-flask-app
```

Ensure Ollama is also installed on the VM, with GPU support if using larger models.

---

## 📈 Scaling Plans

Here are ways to scale and enhance this project:

### 🔄 Multi-Model Switching
- Add dropdown in frontend to select from available Ollama models
- Modify `/query` to dynamically load models

### 📂 File or Image Input
- Expand API to support image uploads (for vision-capable models)
- Add preview and prompt templating in UI

### 🔊 Speech Capabilities
- Integrate with Whisper (speech-to-text) and TTS like Piper
- Enable voice interaction with browser mic

### 🎨 Stable Diffusion
- Run alongside Ollama using [ComfyUI](https://github.com/comfyanonymous/ComfyUI) or [Automatic1111 WebUI]
- Add a toggle in UI to switch between text or image generation modes

### 🧱 Plugin System
- Define pluggable tools (e.g., calculator, document summarizer, PDF reader)
- Add plugin registry and routing to backend

### 🔐 User Authentication
- Add login with JWT or session-based authentication
- Add user history logs, saved prompts, and roles (e.g. viewer, admin)

---

## 📁 File Structure

```
ollama-flask-app/
├── app.py
├── requirements.txt
├── Dockerfile
├── templates/
│   └── index.html
├── static/
│   └── script.js
├── README.md
├── blog.md
```

---

## 🙌 Author

Created by [Jeremy Anderson](https://jeremyanderson.tech) – AI developer, WordPress engineer, cybersecurity researcher, and game dev. Let’s build cool, ethical tech together!