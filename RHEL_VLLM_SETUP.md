# Red Hat AI Inference Server (vLLM) Demo on RHEL

This guide provides step-by-step instructions for setting up vLLM on Red Hat Enterprise Linux (RHEL) and deploying the Red Hat AI Agentic Demo to showcase the features of Red Hat AI Inference Server.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Initial System Setup](#initial-system-setup)
4. [NVIDIA Driver Installation](#nvidia-driver-installation)
5. [Container Runtime Setup](#container-runtime-setup)
6. [vLLM Deployment](#vllm-deployment)
7. [Demo Application Setup](#demo-application-setup)
8. [Testing and Validation](#testing-and-validation)
9. [Troubleshooting](#troubleshooting)

## Overview

This demo showcases Red Hat AI Inference Server (based on vLLM) running an agentic AI workflow that integrates with:
- CRM systems
- PDF generation
- Slack messaging
- Process reports

The architecture includes:
- **UI Frontend**: Web interface for user interactions
- **Llama Stack Server**: Orchestrates LLM interactions and tool selection
- **MCP Servers**: Handle integrations with external systems
- **vLLM Models**: AI models (Granite 3.2-8B and Llama 3.2-3B) for reasoning

## Prerequisites

### Hardware Requirements
- RHEL 9.x server with GPU support
- NVIDIA GPU with minimum 24GiB VRAM (or Intel Habana Gaudi GPU)
- Sufficient CPU and RAM for containerized workloads

### Software Requirements
- Red Hat Enterprise Linux 9.x
- SSH access to the RHEL server
- Hugging Face account and token
- Administrative privileges (sudo access)

### Network Requirements
- Internet connectivity for package installation and model downloads
- SSH access (port 22)
- HTTP access (port 8000 for vLLM, port 8501 for UI)

## Initial System Setup

### 1. Connect to RHEL Server

```bash
# Set your instance IP
instance_ip=<your_server_ip>

# Connect via SSH (adjust key path as needed)
chmod 0600 $HOME/.ssh/vllm_id_ed25519
ssh -i $HOME/.ssh/vllm_id_ed25519 ec2-user@$instance_ip
```

### 2. Install Essential Tools

```bash
# Install tmux for persistent sessions
sudo dnf install -y tmux

# Start a tmux session for persistent work
tmux new-session -d -s vllm-setup
tmux attach-session -t vllm-setup
```

## NVIDIA Driver Installation

### 1. Install Kernel Development Tools

```bash
sudo dnf install -y kernel-devel-matched kernel-headers
sudo dnf config-manager --set-enabled codeready-builder-for-rhel-9-rhui-rpms
```

### 2. Add EPEL Repository

```bash
sudo dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm
```

### 3. Configure NVIDIA CUDA Repository

```bash
sudo dnf config-manager --add-repo https://developer.download.nvidia.com/compute/cuda/repos/rhel9/x86_64/cuda-rhel9.repo
```

### 4. Install NVIDIA Drivers

```bash
sudo dnf install -y nvidia-driver-cuda kmod-nvidia-open-dkms
```

### 5. Reboot System

```bash
sudo reboot now
```

**Note**: Wait for the system to reboot completely before proceeding.

## Container Runtime Setup

### 1. Reconnect and Resume tmux Session

```bash
# Reconnect to server
ssh -i $HOME/.ssh/vllm_id_ed25519 ec2-user@$instance_ip

# Attach to existing tmux session
tmux attach-session -t vllm-setup
```

### 2. Install NVIDIA Container Toolkit

```bash
# Add NVIDIA container toolkit repository
curl -s -L https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo | \
  sudo tee /etc/yum.repos.d/nvidia-container-toolkit.repo

# Enable experimental features
sudo dnf config-manager --enable nvidia-container-toolkit-experimental

# Install container toolkit and Podman
sudo dnf install -y nvidia-container-toolkit podman
```

### 3. Configure CDI for GPU Access

```bash
# Generate CDI specification for GPU access
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml
```

### 4. Test GPU Access

```bash
# Verify GPU is accessible in containers
sudo podman run --rm --device nvidia.com/gpu=all \
  docker.io/nvidia/cuda:11.0.3-base-ubuntu20.04 nvidia-smi
```

**Expected Output**: Should display GPU information including memory, driver version, and CUDA version.

## vLLM Deployment

### 1. Set Up Hugging Face Authentication

```bash
# Export your Hugging Face token (keep this secure!)
export HUGGING_FACE_HUB_TOKEN=<your_actual_huggingface_token>

# Create directory for model cache
mkdir -p $HOME/rhaiis-cache
```

**Note**: Get your Hugging Face token from https://huggingface.co/settings/tokens

### 2. Deploy Red Hat AI Inference Server

Create a new tmux window for the vLLM server:

```bash
# Create new tmux window
# Ctrl+B, then 'c' to create new window
```

Run the Red Hat AI Inference Server container:

```bash
podman run --rm -it \
  --device nvidia.com/gpu=all \
  --security-opt=label=disable \
  --shm-size=4GB -p 8000:8000 \
  --env "HUGGING_FACE_HUB_TOKEN=$HUGGING_FACE_HUB_TOKEN" \
  --env "HF_HUB_OFFLINE=0" \
  --env=VLLM_NO_USAGE_STATS=1 \
  -v $HOME/rhaiis-cache:/opt/app-root/src/.cache \
  registry.redhat.io/rhaiis/vllm-cuda-rhel9:3.0.0 \
  --model RedHatAI/Llama-3.2-1B-Instruct-FP8
```

### 3. Alternative Model Options

For Granite model (adjust based on your GPU memory):

```bash
podman run --rm -it \
  --device nvidia.com/gpu=all \
  --security-opt=label=disable \
  --shm-size=4GB -p 8000:8000 \
  --env "HUGGING_FACE_HUB_TOKEN=$HUGGING_FACE_HUB_TOKEN" \
  --env "HF_HUB_OFFLINE=0" \
  --env=VLLM_NO_USAGE_STATS=1 \
  -v $HOME/rhaiis-cache:/opt/app-root/src/.cache \
  registry.redhat.io/rhaiis/vllm-cuda-rhel9:3.0.0 \
  --model ibm-granite/granite-3.3-2b-instruct
```

## Demo Application Setup

### 1. Clone Demo Repository

Switch to a new tmux window and clone the demo:

```bash
# Create new tmux window: Ctrl+B, then 'c'

# Clone the demo repository
git clone https://github.com/rh-aiservices-bu/rhai-agentic-demo.git
cd rhai-agentic-demo
```

### 2. Set Up Database

```bash
# Start PostgreSQL database
podman run -it --name postgres \
  -e POSTGRES_USER=claimdb \
  -e POSTGRES_PASSWORD=claimdb \
  -v ./local/import.sql:/docker-entrypoint-initdb.d/import.sql:ro \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  -d postgres
```

### 3. Configure Environment Variables

```bash
# Database configuration
export DB_USER=claimdb
export DB_HOST=localhost
export DB_NAME=claimdb
export DB_PASSWORD=claimdb

# Llama Stack configuration
export LLAMA_STACK_PORT=5001
export LLM_URL=http://localhost:8000/v1
export INFERENCE_MODEL=RedHatAI/Llama-3.2-1B-Instruct-FP8
```

### 4. Set Up MCP Servers

#### Install Node.js and Dependencies

```bash
# Install Node.js
sudo dnf install -y nodejs npm

# Set up CRM MCP server
cd mcp-servers/crm
npm install
```

#### Start MCP CRM Service

```bash
npx -y supergateway --stdio "node app/index.js"
```

### 5. Deploy Llama Stack

Create and configure Llama Stack:

```bash
# Create new tmux window for Llama Stack
# Update the run-vllm.yaml configuration if needed

# Run Llama Stack
podman run \
  -it \
  -v ./local/run-vllm.yaml:/root/my-run.yaml \
  -p $LLAMA_STACK_PORT:$LLAMA_STACK_PORT \
  docker.io/llamastack/distribution-remote-vllm:0.2.1 \
  --port $LLAMA_STACK_PORT \
  --yaml-config /root/my-run.yaml \
  --env INFERENCE_MODEL=$INFERENCE_MODEL \
  --env VLLM_URL=$LLM_URL
```

## Testing and Validation

### 1. Verify vLLM Server

```bash
# Test model endpoint
curl http://localhost:8000/v1/models | jq .

# Test chat completion
curl -H 'Content-Type: application/json' \
  http://localhost:8000/v1/chat/completions \
  -d '{
    "model": "RedHatAI/Llama-3.2-1B-Instruct-FP8",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "What do you know about Red Hat, the software company?"}
    ]
  }' | jq -r .choices[0].message.content
```

### 2. Register MCP Tool Groups

```bash
# Register CRM MCP server
curl -X POST -H "Content-Type: application/json" \
  --data '{
    "provider_id": "model-context-protocol",
    "toolgroup_id": "mcp::crm",
    "mcp_endpoint": {"uri": "http://host.containers.internal:8000/sse"}
  }' \
  http://localhost:$LLAMA_STACK_PORT/v1/toolgroups
```

### 3. Deploy and Test UI

```bash
# Build UI container
podman build -t ui -f ui/Containerfile

# Run UI
podman run -p 8501:8501 \
  -e LLAMA_STACK_ENDPOINT=http://host.containers.internal:5001 ui
```

### 4. Sample Test Requests

Test the complete workflow with these sample prompts:

```
Review the current opportunities for ACME
Get a list of support cases for the account
Determine the status of the account, e.g. unhappy, happy etc. based on the cases
Send a slack message to agentic-ai-slack with the status of the account
Generate a PDF document with a summary of the support cases and the account status
Upload the pdf 
Send the link to the agentic-ai-slack channel with the pdf url
```

## Troubleshooting

### Common Issues

1. **GPU Not Detected**
   - Verify NVIDIA drivers: `nvidia-smi`
   - Check CDI configuration: `ls /etc/cdi/`
   - Restart Docker/Podman daemon

2. **Container Permission Issues**
   - Use `--security-opt=label=disable` for SELinux systems
   - Check file permissions on mounted volumes

3. **Model Download Failures**
   - Verify Hugging Face token is valid
   - Check internet connectivity
   - Ensure sufficient disk space for model cache

4. **Memory Issues**
   - Increase `--shm-size` parameter
   - Monitor GPU memory usage with `nvidia-smi`
   - Consider using smaller models for limited VRAM

### Log Analysis

Monitor logs in different tmux windows:
- Window 0: vLLM server logs
- Window 1: Llama Stack logs
- Window 2: MCP server logs
- Window 3: Database and other services

### Performance Tuning

- Adjust `--tensor-parallel-size` based on available GPUs
- Monitor resource usage with `htop` and `nvidia-smi`
- Optimize model loading with appropriate cache settings

## Next Steps

After successful deployment:

1. Explore different model configurations
2. Customize MCP servers for your specific use cases
3. Integrate with your existing systems
4. Scale the deployment for production use
5. Set up monitoring and logging solutions

## Additional Resources

- [Red Hat AI Inference Server Documentation](https://docs.redhat.com/en/documentation/red_hat_ai_inference_server/3.0/)
- [vLLM Documentation](https://docs.vllm.ai/)
- [NVIDIA Container Toolkit Documentation](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/)
