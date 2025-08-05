# Red Hat AI Inference Server (RHAIIS) CRM Demo

> **A comprehensive demonstration of Red Hat AI Inference Server capabilities using IBM Granite models for CRM business intelligence and analytics.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![RHEL 9](https://img.shields.io/badge/RHEL-10-red.svg)](https://www.redhat.com/en/enterprise-linux)

## 🚀 Quick Start

**📋 Recommended AWS Setup**: `g5.4xlarge` EC2 instance with RHEL 10 and 200GB storage

### For New Systems (Complete Setup)
```bash
# 1. Run quick installation (on fresh RHEL 10 with GPU)
curl -sSL https://raw.githubusercontent.com/YOUR_REPO/rhaiis-demo/main/quick-install.sh | bash

# 2. Reboot system to load GPU drivers
sudo reboot

# 3. After reboot, deploy the demo
git clone https://github.com/YOUR_REPO/rhaiis-demo.git
cd rhaiis-demo/app
sudo podman login registry.redhat.io  # Enter Red Hat Developer credentials
./deploy.sh
```

### For Systems with Prerequisites
```bash
# If you already have GPU drivers and container runtime
git clone https://github.com/YOUR_REPO/rhaiis-demo.git
cd rhaiis-demo/app
./deploy.sh
```

## 🎯 What This Demo Shows

This demo showcases an **AI-powered CRM assistant** that can:

- 🔍 **Analyze sales opportunities** and revenue trends
- 📊 **Assess customer account health** and satisfaction metrics  
- 🎫 **Process support case analytics** and identify issues
- 💡 **Provide actionable business intelligence** insights
- 🤖 **Dynamically call database tools** based on natural language queries

### Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Flask API     │◄──►│   Granite AI     │◄──►│   PostgreSQL    │
│   (Port 5000)   │    │   Agent (GPU)    │    │   CRM Database  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

- **Flask REST API**: Handles HTTP requests and routes queries
- **Granite AI Agent**: IBM's 2B parameter model running on GPU
- **PostgreSQL Database**: Sample CRM data with 1,000+ records

## 🎯 Quick Example - AI Agent in Action

Here's a simple example showing how to interact with the AI agent using curl:

### Test the Agentic Behavior

```bash
# Ask the AI about sales opportunities (triggers database tool calling)
curl -X POST "http://localhost:5000/agent/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "What are our top sales opportunities by value?"}'
```

### What Happens Behind the Scenes

1. **Query Analysis**: AI determines this needs sales data
2. **Tool Selection**: Automatically calls `get_opportunities()` database tool  
3. **Data Retrieval**: Fetches real CRM data from PostgreSQL
4. **AI Analysis**: Granite model analyzes the data and generates insights
5. **Business Intelligence**: Returns actionable recommendations

### Expected Response

```json
{
  "response": "Based on the current sales data, you have 1,390 active opportunities worth $45.2M total pipeline value. Your top opportunities by value are:\n\n1. **ERP System Upgrade** - $1.2M (85% probability, Negotiation stage)\n2. **Data Analytics Platform** - $950K (40% probability, Discovery stage) \n3. **Cloud Migration Project** - $750K (75% probability, Proposal stage)\n\nKey insights:\n- 60% of high-value deals are in advanced stages\n- Technology sector represents 40% of pipeline value\n- Average deal size has increased 15% this quarter\n\nRecommendations: Focus sales resources on the ERP upgrade (highest probability) and accelerate the Analytics Platform through discovery phase.",
  "status": "success"
}
```

### More Examples

```bash
# Analyze customer account health
curl -X POST "http://localhost:5000/agent/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Which customers have the highest satisfaction scores?"}'

# Review critical support cases  
curl -X POST "http://localhost:5000/agent/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Show me support cases that need immediate attention"}'

# Get revenue analysis
curl -X POST "http://localhost:5000/agent/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Analyze our revenue trends by industry segment"}'
```

Each query demonstrates the AI agent's ability to:
- 🔍 **Understand natural language** business questions
- 🛠️ **Automatically select appropriate tools** for data access
- 📊 **Analyze real CRM data** from the PostgreSQL database  
- 💡 **Generate actionable insights** and recommendations
- 🚀 **Provide immediate business value** without manual data analysis

## 📋 Prerequisites

### Hardware Requirements
- **AWS EC2**: `g5.4xlarge` recommended for optimal performance
- **GPU**: NVIDIA A10G (24GB VRAM) included with g5.4xlarge
- **vCPUs**: 16 cores
- **RAM**: 64GB
- **Storage**: 200GB+ EBS volume recommended
- **Network**: Enhanced networking enabled


### Software Requirements
- **OS**: Red Hat Enterprise Linux 10, Rocky Linux 10, or CentOS Stream 10
- **Accounts**: Red Hat Developer account (free)
- **Network**: Internet access for package and model downloads

## 🔧 Installation Guide

### Step 1: System Preparation
```bash
# Update system and install essentials
sudo dnf update -y
sudo dnf install -y git tmux wget curl python3 python3-pip podman
```

### Step 2: NVIDIA GPU Drivers (Critical!)
```bash
# Add NVIDIA repository
sudo dnf config-manager --add-repo \
  https://developer.download.nvidia.com/compute/cuda/repos/rhel10/x86_64/cuda-rhel10.repo

# Install GPU drivers (bypass GPG if needed)
sudo dnf install -y --nogpgcheck nvidia-driver nvidia-dkms cuda-drivers

# Install container toolkit
curl -s -L https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo | \
  sudo tee /etc/yum.repos.d/nvidia-container-toolkit.repo
sudo dnf install -y --nogpgcheck nvidia-container-toolkit

# Configure podman for GPU support
sudo nvidia-ctk runtime configure --runtime=podman --config=/usr/share/containers/containers.conf

# REBOOT REQUIRED!
sudo reboot
```

### Step 3: Post-Reboot Verification
```bash
# Verify GPU detection
nvidia-smi

# Test GPU in containers
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml
sudo podman run --rm --device nvidia.com/gpu=all nvidia/cuda:12.0-base-ubuntu20.04 nvidia-smi
```

### Step 4: Deploy Demo
```bash
# Authenticate with Red Hat registry
sudo podman login registry.redhat.io

# Clone and deploy
git clone https://github.com/YOUR_REPO/rhaiis-demo.git
cd rhaiis-demo/app
./deploy.sh
```

## 🧪 Testing the Demo

### Quick Health Check
```bash
curl -X GET "http://localhost:5000/health"
```

### Comprehensive Test Suite
```bash
./test_api.sh
```

## 📖 API Documentation

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check |
| `/agent/chat` | POST | AI-powered chat interface |
| `/db/sales` | GET | Sales opportunities data |
| `/db/accounts` | GET | Customer accounts data |
| `/db/support` | GET | Support cases data |

### Business Intelligence Questions
- "What are our highest value sales opportunities?"
- "Which customers have the best account health scores?"
- "Show me critical support cases that need attention"
- "Analyze revenue trends by industry segment"

## 🔧 Service Management

### Start/Stop Services
```bash
# Start all services
./deploy.sh

# Stop all services  
./stop_services.sh

# Restart services
./stop_services.sh && ./deploy.sh
```

### Monitoring
```bash
# View Flask logs
tail -f flask.log

# Check service status
sudo podman ps
ps aux | grep python.*app.py

# Monitor GPU usage
watch -n 1 nvidia-smi
```

## 🐛 Troubleshooting

### Common Issues

1. **GPU Not Detected**
   ```bash
   # Check driver installation
   nvidia-smi
   # If fails, reinstall drivers and reboot
   ```

2. **Container Registry Access Denied**
   ```bash
   # Re-authenticate with Red Hat
   sudo podman login registry.redhat.io
   ```

3. **Out of Memory**
   ```bash
   # Check available memory
   free -h
   # Add swap if needed
   sudo fallocate -l 8G /swapfile && sudo chmod 600 /swapfile
   sudo mkswap /swapfile && sudo swapon /swapfile
   ```

4. **Port Conflicts**
   ```bash
   # Kill processes on ports 5000/5432
   sudo fuser -k 5000/tcp
   sudo fuser -k 5432/tcp
   ```

For complete troubleshooting guide, see [TROUBLESHOOTING.md](app/TROUBLESHOOTING.md).

## 📊 Performance Metrics

### Expected Performance
- **AI Response Time**: 2-5 seconds for business queries
- **Database Queries**: <500ms for CRM data retrieval
- **Memory Usage**: ~15GB RAM, ~8GB GPU VRAM
- **Model Loading**: 2-5 minutes first time, 30s subsequent starts

### Resource Utilization
| Component | CPU Usage | RAM Usage | GPU VRAM |
|-----------|-----------|-----------|----------|
| PostgreSQL | 5-10% | 2GB | - |
| Granite Model | 25-40% | 12GB | 8GB |
| Flask API | 2-5% | 1GB | - |

## 🏗️ Architecture Details

### AI Agent Workflow
1. **Query Analysis**: Determines if database access needed
2. **Tool Selection**: Chooses appropriate database tool
3. **Data Retrieval**: Executes SQL queries via Python tools
4. **AI Processing**: Granite model analyzes data and generates insights
5. **Response Generation**: Returns actionable business intelligence

### Database Schema
- **Accounts**: 951 customer companies with industry/revenue data
- **Opportunities**: 1,390 sales deals with pipeline stages
- **Support Cases**: Customer service tickets with priorities
- **Health Metrics**: Account satisfaction and engagement scores

## 🔒 Security Considerations

- **Development Mode**: Demo runs Flask in development mode
- **Default Credentials**: Uses demo database credentials
- **Network Binding**: API accessible on all interfaces for testing
- **Production Use**: Implement proper authentication, HTTPS, and firewall rules

## 📚 Additional Resources

- **[Deployment Checklist](app/DEPLOYMENT_CHECKLIST.md)**: Step-by-step deployment verification
- **[Troubleshooting Guide](app/TROUBLESHOOTING.md)**: Comprehensive problem resolution
- **[API Examples](app/test_api.sh)**: Complete API testing script
- **[Project Structure](PROJECT_STRUCTURE.md)**: Detailed file organization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: GitHub Issues for bug reports
- **Questions**: GitHub Discussions for questions
- **Documentation**: Check troubleshooting guide first

---

**⭐ Don't forget to star this repository if it helps with your Red Hat AI Inference Server evaluation!**
