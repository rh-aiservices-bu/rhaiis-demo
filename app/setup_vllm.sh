#!/bin/bash

# Script to setup the vLLM server with Granite model

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Configuration
MODEL_NAME="ibm-granite/granite-3.3-2b-instruct"
VLLM_PORT=8000
CACHE_DIR="$HOME/rhaiis-cache"

# Check if Hugging Face token is set
if [ -z "$HUGGING_FACE_HUB_TOKEN" ]; then
    log_error "HUGGING_FACE_HUB_TOKEN environment variable is not set"
    log_info "Please set your Hugging Face token:"
    log_info "export HUGGING_FACE_HUB_TOKEN='your_token_here'"
    exit 1
fi

# Create cache directory
log_info "Creating model cache directory: $CACHE_DIR"
mkdir -p "$CACHE_DIR"

# Check if vLLM container already exists and remove it
if podman ps -a --format "{{.Names}}" | grep -q "^vllm-demo$"; then
    log_info "Stopping and removing existing vLLM container..."
    podman stop vllm-demo 2>/dev/null || true
    podman rm vllm-demo 2>/dev/null || true
fi

# Start vLLM in a tmux session
log_info "Starting vLLM server with model: $MODEL_NAME"
log_info "This may take several minutes to download and load the model..."

# Create tmux session for vLLM
tmux new-session -d -s vllm-demo

# Send command to tmux session
tmux send-keys -t vllm-demo "podman run --rm -it \\
  --name vllm-demo \\
  --device nvidia.com/gpu=all \\
  --security-opt=label=disable \\
  --shm-size=4GB -p $VLLM_PORT:$VLLM_PORT \\
  --env \"HUGGING_FACE_HUB_TOKEN=$HUGGING_FACE_HUB_TOKEN\" \\
  --env \"HF_HUB_OFFLINE=0\" \\
  --env=VLLM_NO_USAGE_STATS=1 \\
  -v $CACHE_DIR:/opt/app-root/src/.cache \\
  registry.redhat.io/rhaiis/vllm-cuda-rhel9:3.0.0 \\
  --model $MODEL_NAME \\
  --host 0.0.0.0 \\
  --port $VLLM_PORT" Enter

log_success "vLLM server started in tmux session 'vllm-demo'"
log_info "Monitor progress with: tmux attach-session -t vllm-demo"
log_info "Detach from tmux with: Ctrl+B, then D"

# Wait a moment for container to start
sleep 5

# Check if container is running
if podman ps --format "{{.Names}}" | grep -q "^vllm-demo$"; then
    log_success "vLLM container is running"
else
    log_error "vLLM container failed to start"
    log_info "Check logs with: tmux attach-session -t vllm-demo"
    exit 1
fi
