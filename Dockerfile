ARG OLLAMA_TAG=latest
ARG MODEL_NAME=huihui-q5

# Stage 1: download model and bake into Ollama
FROM ollama/ollama:${OLLAMA_TAG} AS builder
ARG MODEL_NAME

ENV OLLAMA_HOST=0.0.0.0:11434

RUN apt-get update -qq && \
    apt-get install -y -qq python3 python3-pip curl zstd && \
    pip3 install --quiet huggingface_hub

COPY download.py /build/download.py
COPY Modelfile /build/Modelfile

WORKDIR /build

# Download the Q5 GGUF from Hugging Face
RUN python3 /build/download.py

# Start Ollama, wait for it, import the model, verify
RUN sh -c 'ollama serve >/tmp/ollama.log 2>&1 & \
    for i in $(seq 1 120); do \
      ollama list >/dev/null 2>&1 && echo "Ollama ready after ${i}s" && break; \
      sleep 1; \
    done && \
    ollama create huihui-q5 -f /build/Modelfile && \
    ollama list'

# Stage 2: clean runtime image with baked model
FROM ollama/ollama:${OLLAMA_TAG}
ENV OLLAMA_HOST=0.0.0.0:11434
ENV MODEL_NAME=huihui-q5

RUN apt-get update -qq && \
    apt-get install -y -qq python3 python3-pip curl zstd && \
    pip3 install --quiet runpod requests && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.ollama /root/.ollama
COPY handler.py /app/handler.py
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh && sed -i 's/\r//' /app/start.sh

WORKDIR /app
EXPOSE 11434
CMD ["/app/start.sh"]
