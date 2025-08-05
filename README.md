# Red Hat AI Inference Server (RHAIIS) Demo

A simplified demonstration of an AI-powered business intelligence agent using IBM Granite models via vLLM on Red Hat Enterprise Linux (RHEL).

## Quick Start

For RHEL 10 with GPU support:

```bash
# Clone the repository
git clone https://github.com/rh-aiservices-bu/rhaiis-demo.git
cd rhaiis-demo

# Run the quick installation script
./quick-install.sh

# Reboot to load GPU drivers
sudo reboot

# After reboot, deploy the demo
cd rhaiis-demo/app
sudo podman login registry.redhat.io  # Use your Red Hat credentials
./deploy.sh
```

## Prerequisites

### Hardware
- **Recommended**: AWS EC2 `g5.4xlarge` instance (16 vCPU, 64GB RAM, NVIDIA A10G GPU)
- **Storage**: 200GB+ SSD recommended
- **GPU**: NVIDIA GPU with at least 8GB VRAM for Granite model inference

### Software
- **OS**: Red Hat Enterprise Linux 10.x
- **Access**: Red Hat subscription (for container registry access)

## Installation

### Option 1: Automated Installation (Recommended)

Use the provided quick-install script that handles all dependencies:

```bash
git clone https://github.com/rh-aiservices-bu/rhaiis-demo.git
cd rhaiis-demo
./quick-install.sh
sudo reboot
```

### Option 2: Manual Installation

#### 1. Install Basic Tools
```bash
sudo dnf update -y
sudo dnf install -y git tmux wget curl python3 python3-pip podman
```

#### 2. Install NVIDIA GPU Drivers

**For RHEL 10**, use RPM Fusion repositories (tested working method):

```bash
# Install EPEL and RPM Fusion repositories
sudo dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-10.noarch.rpm
sudo dnf install -y https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-$(rpm -E %rhel).noarch.rpm
sudo dnf install -y https://mirrors.rpmfusion.org/nonfree/el/rpmfusion-nonfree-release-$(rpm -E %rhel).noarch.rpm

# Install kernel development packages
sudo dnf install -y kernel-devel kernel-headers dkms gcc make

# Install NVIDIA drivers
sudo dnf install -y akmod-nvidia xorg-x11-drv-nvidia-cuda
```

#### 3. Install NVIDIA Container Toolkit
```bash
curl -s -L https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo | \
  sudo tee /etc/yum.repos.d/nvidia-container-toolkit.repo
sudo dnf install -y --nogpgcheck nvidia-container-toolkit
```

#### 4. Reboot System
```bash
sudo reboot
```

#### 5. Verify GPU Installation
After reboot, verify NVIDIA drivers are working:
```bash
nvidia-smi
```

You should see your GPU listed with driver information.

## Deployment

### 1. Login to Red Hat Registry
```bash
sudo podman login registry.redhat.io
```
Use your Red Hat account credentials.

### 2. Deploy the Demo
```bash
cd rhaiis-demo/app
./deploy.sh
```

The deployment script will:
- Start PostgreSQL database with sample CRM data
- Launch vLLM server with IBM Granite model
- Start Flask API server for the AI agent

### 3. Verify Deployment
```bash
./test_api.sh
```

## Usage

### API Endpoints

**Health Check:**
```bash
curl http://localhost:5000/health
```

**Chat with AI Agent:**
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me our top 5 sales opportunities"}'
```

**Database Endpoints:**
- `GET /opportunities` - List sales opportunities
- `GET /support_cases` - List support cases  
- `GET /accounts/{account_id}` - Get account details
- `POST /accounts/{account_id}/health` - Analyze account health

### Example AI Queries

The AI agent can handle natural language queries like:

- **Sales Analysis**: "What are our top 5 sales opportunities this quarter?"
- **Support Intelligence**: "Show me all critical support cases"
- **Account Health**: "Analyze the health of account ACCT-001"
- **Cross-functional**: "Which accounts have both high-value opportunities and open support cases?"

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Client    │───▶│   Flask API      │───▶│   PostgreSQL    │
│                 │    │  (Port 5000)     │    │   Database      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   vLLM Server    │
                       │ (Granite Model)  │
                       │  (Port 8000)     │
                       └──────────────────┘
```

## Components

- **Flask API**: RESTful web service handling chat and data requests
- **Granite AI Agent**: IBM Granite model with tool-calling capabilities
- **vLLM Server**: High-performance inference server for LLM
- **PostgreSQL Database**: Sample CRM data (opportunities, accounts, support cases)
- **Business Intelligence Tools**: CRM data analysis and account health scoring

## Stopping the Demo

```bash
cd rhaiis-demo/app
./stop_services.sh
```

## Troubleshooting

### GPU Issues
- Verify drivers: `nvidia-smi`
- Check GPU access: `sudo podman run --rm --gpus all nvidia/cuda:12.0-base-ubuntu20.04 nvidia-smi`

### Container Issues  
- Check podman status: `podman ps -a`
- View logs: `podman logs <container_name>`
- Restart services: `./stop_services.sh && ./deploy.sh`

### vLLM Issues
- Check memory usage: `free -h`
- Verify model download: `ls -la ~/.cache/huggingface/hub/`
- Monitor vLLM logs: `podman logs vllm-server`

### Database Issues
- Check PostgreSQL status: `podman exec -it postgres-db psql -U demo -d crm_demo -c "\dt"`
- Reset database: Remove `postgres-data` volume and redeploy

## NVIDIA Driver Installation Details

For detailed NVIDIA driver installation instructions and troubleshooting, see [README_NVIDIA_SECTION.md](README_NVIDIA_SECTION.md).

### Key Points for RHEL 10:
- **Use RPM Fusion repositories** (not NVIDIA CUDA repos)
- Install `akmod-nvidia` package for automatic kernel module building
- Requires EPEL repository for dependencies
- Reboot required after installation

## Contributing

This demo is designed for educational and demonstration purposes. For production deployments, consider:

- Implementing proper authentication and authorization
- Adding SSL/TLS encryption
- Setting up monitoring and logging
- Configuring high availability
- Implementing proper secrets management

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
