#!/usr/bin/env bash
set -euo pipefail

export OLLAMA_HOST=0.0.0.0:11434
export MODEL_NAME=${MODEL_NAME:-huihui-q5}

echo "[start.sh] Starting Ollama server..."
ollama serve &
OLLAMA_PID=$!

echo "[start.sh] Waiting for Ollama API..."
for i in $(seq 1 120); do
  if curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "[start.sh] Ollama ready after ${i}s"
    break
  fi
  sleep 1
done

echo "[start.sh] Installed models:"
curl -s http://localhost:11434/api/tags

echo "[start.sh] Starting RunPod handler..."
exec python3 /app/handler.py
