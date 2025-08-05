#!/bin/bash

echo "[INFO] Setting up vLLM server for Granite model..."

# Create model cache directory
MODEL_CACHE_DIR="$HOME/rhaiis-cache"
mkdir -p "$MODEL_CACHE_DIR"
echo "[INFO] Created model cache directory: $MODEL_CACHE_DIR"

# Stop any existing vLLM container
sudo podman stop granite-vllm 2>/dev/null || true
sudo podman rm granite-vllm 2>/dev/null || true

# Start vLLM server container
echo "[INFO] Starting vLLM server with model: ibm-granite/granite-3.3-2b-instruct"
echo "[INFO] This may take several minutes to download and load the model..."

sudo podman run -d \
  --name granite-vllm \
  --device nvidia.com/gpu=all \
  -p 8000:8000 \
  -v "$MODEL_CACHE_DIR:/root/.cache/huggingface" \
  -e HF_TOKEN="${HF_TOKEN:-}" \
  quay.io/ai-lab/vllm:latest \
  --model ibm-granite/granite-3.3-2b-instruct \
  --host 0.0.0.0 \
  --port 8000 \
  --served-model-name ibm-granite/granite-3.3-2b-instruct

# Wait a moment and check if container started
sleep 5

if sudo podman ps | grep -q granite-vllm; then
    echo "[SUCCESS] vLLM server container started successfully"
    echo "[INFO] Monitor logs with: sudo podman logs -f granite-vllm"
    echo "[INFO] The model may take several minutes to download and load"
    echo "[INFO] Check status at: http://localhost:8000/health"
else
    echo "[ERROR] vLLM container failed to start"
    echo "[INFO] Check logs with: sudo podman logs granite-vllm"
    exit 1
fi
