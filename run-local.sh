#!/usr/bin/env bash
set -euo pipefail
IMAGE="${1:-ollama-huihui-q5:local}"
NAME="ollama-huihui-q5-test"
docker rm -f "${NAME}" 2>/dev/null || true
docker run -d --name "${NAME}" -p 11434:11434 -e MODEL_NAME=huihui-q5 "${IMAGE}"
echo "Waiting for API..."
until curl -sf http://localhost:11434/api/tags >/dev/null; do sleep 2; done
echo "Models:"
curl -s http://localhost:11434/api/tags | python3 -m json.tool
