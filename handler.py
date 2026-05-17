import runpod
import requests
import os

OLLAMA_BASE = "http://localhost:11434"
MODEL_NAME = os.environ.get("MODEL_NAME", "huihui-q5")


def generate(payload):
    resp = requests.post(
        f"{OLLAMA_BASE}/api/generate",
        json={
            "model": MODEL_NAME,
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
        "model": data.get("model", MODEL_NAME),
        "done": data.get("done", True),
        "prompt_eval_count": data.get("prompt_eval_count"),
        "eval_count": data.get("eval_count"),
    }


def chat(payload):
    resp = requests.post(
        f"{OLLAMA_BASE}/api/chat",
        json={
            "model": MODEL_NAME,
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
        "model": data.get("model", MODEL_NAME),
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
    except Exception as e:
        return {"error": str(e), "ok": False}


runpod.serverless.start({"handler": handler})
