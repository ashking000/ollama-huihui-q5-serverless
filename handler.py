import runpod
import requests
import os
import time
import sys

OLLAMA_BASE = "http://localhost:11434"
MODEL_NAME = os.environ.get("MODEL_NAME", "huihui-q5")


def wait_for_model(timeout=300):
    """Block until Ollama is up AND the model appears in /api/tags."""
    print(f"[handler] Waiting for Ollama + model '{MODEL_NAME}'...", flush=True)
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=5)
            if resp.status_code == 200:
                models = [m["name"] for m in resp.json().get("models", [])]
                print(f"[handler] Available models: {models}", flush=True)
                base = MODEL_NAME.split(":")[0]
                for m in models:
                    if m == MODEL_NAME or m.startswith(base):
                        print(f"[handler] Model '{m}' is ready.", flush=True)
                        return True
        except Exception:
            pass
        time.sleep(3)
    print(f"[handler] ERROR: model '{MODEL_NAME}' not found after {timeout}s.", flush=True)
    return False


def generate(payload):
    model = payload.get("model", MODEL_NAME)
    resp = requests.post(
        f"{OLLAMA_BASE}/api/generate",
        json={
            "model": model,
            "prompt": payload.get("prompt", ""),
            "stream": False,
            "options": {
                "num_ctx": payload.get("num_ctx", 8192),
                "temperature": payload.get("temperature", 0.7),
                "top_p": payload.get("top_p", 0.9),
            },
        },
        timeout=300,
    )
    resp.raise_for_status()
    data = resp.json()
    return {
        "response": data.get("response", ""),
        "model": data.get("model", model),
        "done": data.get("done", True),
        "prompt_eval_count": data.get("prompt_eval_count"),
        "eval_count": data.get("eval_count"),
    }


def chat(payload):
    model = payload.get("model", MODEL_NAME)
    resp = requests.post(
        f"{OLLAMA_BASE}/api/chat",
        json={
            "model": model,
            "messages": payload.get("messages", []),
            "stream": False,
            "options": {
                "num_ctx": payload.get("num_ctx", 8192),
                "temperature": payload.get("temperature", 0.7),
                "top_p": payload.get("top_p", 0.9),
            },
        },
        timeout=300,
    )
    resp.raise_for_status()
    data = resp.json()
    return {
        "message": data.get("message", {}),
        "model": data.get("model", model),
        "done": data.get("done", True),
        "prompt_eval_count": data.get("prompt_eval_count"),
        "eval_count": data.get("eval_count"),
    }


def handler(job):
    job_input = job.get("input", {})
    mode = job_input.get("mode", "generate")
    try:
        if mode == "chat":
            return chat(job_input)
        return generate(job_input)
    except requests.exceptions.HTTPError as e:
        return {"error": f"Ollama {e.response.status_code}: {e.response.text}", "ok": False}
    except Exception as e:
        return {"error": str(e), "ok": False}


# Block until Ollama has the model ready before accepting any RunPod jobs
if not wait_for_model(timeout=300):
    print("[handler] FATAL: model not ready. Exiting.", flush=True)
    sys.exit(1)

print(f"[handler] Ready. Serving model='{MODEL_NAME}'", flush=True)
runpod.serverless.start({"handler": handler})
