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

# ⚠️ IMPORTANT: Login to Red Hat registry (REQUIRED)
sudo podman login registry.redhat.io
# Enter your Red Hat account username and password

# Deploy the demo
./deploy.sh
```

## Prerequisites

### Hardware
- **Recommended**: AWS EC2 `g5.4xlarge` instance (16 vCPU, 64GB RAM, NVIDIA A10G GPU)
- **Minimum**: System with NVIDIA GPU (8GB+ VRAM recommended)
- **Storage**: 200GB+ SSD recommended
- **GPU**: NVIDIA GPU with at least 8GB VRAM for Granite model inference

### Software
- **OS**: Red Hat Enterprise Linux 10.x
- **Access**: **Red Hat subscription with registry access** (required for container images)

⚠️ **Red Hat Account Required**: You need a valid Red Hat account to access the container registry. The demo uses Red Hat certified container images.

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

### 1. Login to Red Hat Registry (REQUIRED)

⚠️ **Critical Step**: Before deployment, you MUST login to the Red Hat container registry:

```bash
sudo podman login registry.redhat.io
```

**When prompted, enter:**
- **Username**: Your Red Hat account username
- **Password**: Your Red Hat account password

**Why this is required:**
- The demo uses Red Hat certified PostgreSQL container images
- Red Hat registry requires authentication for access
- Without login, deployment will fail with authentication errors

**Don't have a Red Hat account?**
- Create one at: https://access.redhat.com/
- Free developer accounts are available
- Required for accessing Red Hat container registry

### 2. Deploy the Demo
```bash
cd rhaiis-demo/app
./deploy.sh
```

The deployment script will:
- Install Python dependencies (PyTorch, Transformers, etc.)
- Start PostgreSQL database with sample CRM data
- Load IBM Granite model with GPU acceleration
- Start Flask API server for the AI agent

### 3. Verify Deployment
```bash
./test_api.sh
```

This comprehensive test suite validates:
- Service health and API endpoints
- Database connectivity and data access
- AI agent intelligence and business analysis
- GPU acceleration and system performance

## Usage

### API Endpoints

**Health Check:**
```bash
curl http://localhost:5000/health
```

**Chat with AI Agent:**
```bash
curl -X POST http://localhost:5000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me our top 5 sales opportunities"}'
```

**Database Endpoints:**
- `GET /db/sales` - List sales opportunities
- `GET /db/support` - List support cases  
- `GET /db/accounts` - Get account details

### Example AI Queries

The AI agent can handle natural language queries like:

- **Sales Analysis**: "What are our top 5 sales opportunities this quarter?"
- **Support Intelligence**: "Show me all critical support cases"
- **Account Health**: "Analyze the health of our customer accounts"
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
                       │ IBM Granite Model│
                       │ (GPU Accelerated)│
                       │   Transformers   │
                       └──────────────────┘
```

## Components

- **Flask API**: RESTful web service handling chat and data requests
- **Granite AI Agent**: IBM Granite model with tool-calling capabilities
- **GPU Acceleration**: NVIDIA CUDA support via PyTorch
- **PostgreSQL Database**: Sample CRM data (opportunities, accounts, support cases)
- **Business Intelligence Tools**: CRM data analysis and account health scoring

## Stopping the Demo

```bash
cd rhaiis-demo/app
./stop_services.sh
```

## Troubleshooting

### Red Hat Registry Issues

**Error: "unauthorized: authentication required"**
```bash
# Solution: Login to Red Hat registry
sudo podman login registry.redhat.io
```

**Error: "invalid username/password"**
- Verify your Red Hat account credentials
- Ensure account has access to container registry
- Try logging in via web: https://access.redhat.com/

### GPU Issues
- Verify drivers: `nvidia-smi`
- Check GPU memory: Look for ~5GB usage during model loading
- Temperature monitoring: Ensure GPU temps are reasonable (<80°C)

### Container Issues  
- Check podman status: `podman ps -a`
- View logs: `podman logs <container_name>`
- Restart services: `./stop_services.sh && ./deploy.sh`

### Model Loading Issues
- **Out of memory**: Requires 8GB+ GPU VRAM for Granite model
- **Slow loading**: Initial model download can take 5-10 minutes
- **Connection timeout**: Check internet connectivity for model download

### Database Issues
- Check PostgreSQL status: `podman exec -it postgres-db psql -U crm_user -d crm_db -c "\dt"`
- Reset database: Remove postgres-data volume and redeploy

## Performance Expectations

### Model Loading Time
- **First run**: 5-10 minutes (model download + loading)
- **Subsequent runs**: 1-2 minutes (loading from cache)
- **GPU memory usage**: ~5.2GB for Granite model

### Query Response Times
- **Simple queries**: 1-3 seconds
- **Complex analysis**: 10-20 seconds
- **Database queries**: <1 second

## NVIDIA Driver Installation Details

For detailed NVIDIA driver installation instructions and troubleshooting, see [README_NVIDIA_SECTION.md](README_NVIDIA_SECTION.md).

### Key Points for RHEL 10:
- **Use RPM Fusion repositories** (not NVIDIA CUDA repos)
- Install `akmod-nvidia` package for automatic kernel module building
- Requires EPEL repository for dependencies
- Reboot required after installation

## Security Considerations

This demo is designed for educational and demonstration purposes. For production deployments, consider:

- Implementing proper authentication and authorization
- Adding SSL/TLS encryption for API endpoints
- Setting up monitoring and logging
- Configuring proper secrets management for database credentials
- Implementing rate limiting and input validation
- Using non-root containers where possible

## Contributing

This project demonstrates Red Hat's enterprise AI capabilities. For issues or improvements:

1. Check existing documentation and troubleshooting guides
2. Verify system requirements and prerequisites
3. Test with the provided test suite
4. Review logs for specific error messages

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

---

## Quick Reference

**Essential Commands:**
```bash
# Install and setup
./quick-install.sh && sudo reboot

# Login to registry (REQUIRED)
sudo podman login registry.redhat.io

# Deploy demo
cd app && ./deploy.sh

# Test everything
./test_api.sh

# Monitor GPU
nvidia-smi

# Stop services
./stop_services.sh
```

**Important URLs:**
- Red Hat Account: https://access.redhat.com/
- Demo API: http://localhost:5000/health
- AI Chat: POST http://localhost:5000/agent/chat
