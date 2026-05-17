# ollama-huihui-q5-serverless

RunPod Serverless worker with **Ollama + Huihui-Qwen3.5-35B Q5_K_M GGUF baked into the Docker image**.

Model is downloaded from Hugging Face **during Docker build** — container starts instantly with zero per-request model download.

## Model

| Key | Value |
|---|---|
| HF Repo | `ashish8033ash00/Huihui-Qwen3.5-35B-A3B-abliterated-GGUF` |
| File | `Huihui-Qwen3.5-35B-A3B-abliterated.Q5_K_M.gguf` |
| Ollama model name | `huihui-q5` |

## Repo structure

```
.
├── .github/workflows/ghcr.yml   # GitHub Actions: build + push to GHCR
├── .dockerignore
├── Dockerfile                   # multi-stage, downloads GGUF + bakes model
├── Modelfile                    # Ollama Modelfile
├── handler.py                   # RunPod serverless handler
├── start.sh                     # entrypoint: Ollama + handler
├── run-local.sh                 # local test helper
├── test_input.json              # RunPod test payload (generate)
└── test_input_chat.json         # RunPod test payload (chat)
```

## One-time setup: enable workflow permissions

1. Go to **Settings → Actions → General → Workflow permissions**
2. Select **Read and write permissions** → Save
3. Push to `main` — workflow auto-builds and pushes to:
   ```
   ghcr.io/ashking000/ollama-huihui-q5:latest
   ```

## Local build + test

```bash
# Build (downloads ~24GB model during build — needs ~50GB disk)
docker build --platform linux/amd64 -t ollama-huihui-q5:local .

# Run
./run-local.sh ollama-huihui-q5:local

# Quick API test
curl -s http://localhost:11434/api/generate \
  -H 'Content-Type: application/json' \
  -d '{"model":"huihui-q5","prompt":"Say hello","stream":false}'
```

## RunPod Serverless deployment

1. **RunPod → Serverless → New Endpoint**
2. **Container Image**: `ghcr.io/ashking000/ollama-huihui-q5:latest`
3. **Container Disk**: `80 GB`
4. **GPU**: 24GB+ VRAM (A40, A100, RTX 3090)
5. **Env vars**:
   ```
   MODEL_NAME = huihui-q5
   ```
6. Deploy → test in Requests tab

## API payload examples

### Generate
```json
{
  "input": {
    "mode": "generate",
    "prompt": "Who are you?",
    "num_ctx": 4096,
    "temperature": 0.7
  }
}
```

### Chat
```json
{
  "input": {
    "mode": "chat",
    "messages": [{"role": "user", "content": "Who are you?"}],
    "num_ctx": 4096,
    "temperature": 0.7
  }
}
```
