# Ollama Flask Web App

A simple self-hosted web app using Flask to interact with an Ollama language model.

## 🧪 Local Development

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
python app.py
```

Visit `http://localhost:5000`

## 🔒 Secure Public Access (with Cloudflare Tunnel)

To securely expose your app without opening ports on your router:

1. [Install Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/)
2. Authenticate with `cloudflared tunnel login`
3. Run your tunnel:

```bash
cloudflared tunnel --url http://localhost:5000
```

4. You'll get a public `https://your-tunnel-id.trycloudflare.com` link you can use for testing.

## 🐳 Optional Docker

```bash
docker build -t ollama-flask-app .
docker run -p 5000:5000 ollama-flask-app
```

This setup makes switching to a cloud host like DigitalOcean, Linode, or AWS easy.