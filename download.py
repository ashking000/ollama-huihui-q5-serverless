from huggingface_hub import hf_hub_download
import os

path = hf_hub_download(
    repo_id="ashish8033ash00/Huihui-Qwen3.5-35B-A3B-abliterated-GGUF",
    filename="Huihui-Qwen3.5-35B-A3B-abliterated.Q5_K_M.gguf",
    local_dir="/build/model-files"
)
print("Downloaded to:", path)
