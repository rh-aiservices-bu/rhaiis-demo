# Red Hat AI Inference Server (RHAIIS) CRM Demo

> **A comprehensive demonstration of Red Hat AI Inference Server capabilities using IBM Granite models for CRM business intelligence and analytics.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![RHEL 10](https://img.shields.io/badge/RHEL-10-red.svg)](https://www.redhat.com/en/enterprise-linux)

## 🚀 Complete Installation Guide

### 📋 Prerequisites
- **AWS EC2**: `g5.4xlarge` instance recommended
- **OS**: Red Hat Enterprise Linux 10
- **Storage**: 200GB+ EBS volume  
- **Account**: Red Hat Developer account (free)

### Step 1: Launch AWS Instance
Create a `g5.4xlarge` EC2 instance with:
- **AMI**: Red Hat Enterprise Linux 10
- **Storage**: 200GB GP3 EBS volume
- **Security Group**: Allow SSH (port 22) and HTTP (port 5000)
- **Key Pair**: For SSH access

### Step 2: Clone Repository and Run Setup
```bash
# SSH into your instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Clone the demo repository
git clone https://github.com/rh-aiservices-bu/rhaiis-demo.git
cd rhaiis-demo

# Run the automated setup script (installs GPU drivers and dependencies)
./quick-install.sh

# Reboot to load GPU drivers (CRITICAL!)
sudo reboot
```

### Step 3: Deploy the Demo
```bash
# SSH back in after reboot
ssh -i your-key.pem ec2-user@your-instance-ip
cd rhaiis-demo/app

# Authenticate with Red Hat registry
sudo podman login registry.redhat.io
# Enter your Red Hat Developer credentials

# Deploy the complete demo
./deploy.sh
```

### Step 4: Verify Installation
```bash
# Health check (should return: {"status":"AI Agent Service is running"})
curl -X GET "http://localhost:5000/health"

# Run comprehensive test suite
./test_api.sh
```

### 🎉 Success!
Your RHAIIS CRM demo is now running with:
- **GPU-accelerated AI**: IBM Granite model on NVIDIA A10G
- **Live CRM database**: 1,390+ sales opportunities, 951+ accounts
- **REST API**: Ready for business intelligence queries

---

## 🔄 If You Already Have Prerequisites Installed

If your system already has GPU drivers and container runtime:

```bash
# Quick deployment only
git clone https://github.com/rh-aiservices-bu/rhaiis-demo.git
cd rhaiis-demo/app
sudo podman login registry.redhat.io
./deploy.sh
```

---
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

## 📋 System Requirements

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

## 🔧 Manual Installation Guide

### Step 1: System Preparation
```bash
# Update system and install essentials
sudo dnf update -y
sudo dnf install -y git tmux wget curl python3 python3-pip podman
```

### Step 2: NVIDIA GPU Drivers (Critical!)

> **⚠️ GPU acceleration is essential** for optimal AI performance

#### Quick Installation (RHEL 10)
```bash
# Install EPEL and RPM Fusion repositories
sudo dnf install https://dl.fedoraproject.org/pub/epel/epel-release-latest-10.noarch.rpm -y
sudo dnf install \
    https://download1.rpmfusion.org/free/el/rpmfusion-free-release-$(rpm -E %rhel).noarch.rpm \
    https://download1.rpmfusion.org/nonfree/el/rpmfusion-nonfree-release-$(rpm -E %rhel).noarch.rpm -y

# Install NVIDIA drivers and CUDA tools
sudo dnf install akmod-nvidia xorg-x11-drv-nvidia-cuda -y

# Build kernel modules and reboot
sudo systemctl start akmods
sudo reboot
```

#### Verification
```bash
# After reboot, verify GPU is detected
nvidia-smi
```

📖 **For detailed installation guide, troubleshooting, and alternative methods**: [NVIDIA Installation Guide](README_NVIDIA_SECTION.md)

### Step 3: Deploy Demo
```bash
# After reboot, verify GPU is working
nvidia-smi
```

```bash
# Clone repository (if not done already)
git clone https://github.com/rh-aiservices-bu/rhaiis-demo.git
cd rhaiis-demo/app

# Deploy the demo
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


### NVIDIA GPU Driver Installation (RHEL 10)

> **⚠️ Critical for GPU acceleration**: These steps are required for optimal performance

#### Prerequisites
- RHEL 10 system with NVIDIA GPU
- Administrative (sudo) access
- Internet connection for package downloads

#### Step-by-Step Installation

1. **Install EPEL Repository**
   ```bash
   sudo dnf install https://dl.fedoraproject.org/pub/epel/epel-release-latest-10.noarch.rpm -y
   ```

2. **Install RPM Fusion Repositories**
   ```bash
   sudo dnf install \
       https://download1.rpmfusion.org/free/el/rpmfusion-free-release-$(rpm -E %rhel).noarch.rpm \
       https://download1.rpmfusion.org/nonfree/el/rpmfusion-nonfree-release-$(rpm -E %rhel).noarch.rpm -y
   ```

3. **Install NVIDIA Drivers and Tools**
   ```bash
   # Install the main NVIDIA driver package with automatic kernel module building
   sudo dnf install akmod-nvidia -y
   
   # Install additional NVIDIA utilities and CUDA support
   sudo dnf install xorg-x11-drv-nvidia-cuda -y
   ```

4. **Build and Load Kernel Modules**
   ```bash
   # Start the akmods service to build NVIDIA kernel modules
   sudo systemctl start akmods
   
   # Verify kernel modules were built successfully
   ls /lib/modules/$(uname -r)/extra/nvidia*
   ```

5. **Reboot System**
   ```bash
   sudo reboot
   ```

6. **Verify Installation**
   ```bash
   # Check NVIDIA driver version and GPU status
   nvidia-smi
   
   # Verify kernel modules are loaded
   lsmod | grep nvidia
   ```

#### Expected Output
After successful installation, `nvidia-smi` should display:
```
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 575.64.05              Driver Version: 575.64.05      CUDA Version: 12.9     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  Tesla T4                       Off |   00000000:00:1E.0 Off |                    0 |
| N/A   31C    P8             13W /   70W |       0MiB /  15360MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
```

#### Troubleshooting
- **If `nvidia-smi` command not found**: Install `xorg-x11-drv-nvidia-cuda` package
- **If kernel modules don't build**: Ensure matching `kernel-devel` package is installed
- **If installation fails**: Check system logs with `journalctl -u akmods`

#### GPU Verification for This Demo
Once drivers are installed, the deployment script will automatically detect GPU acceleration:
```bash
./deploy.sh
# Should show: "✅ NVIDIA GPU detected: Tesla T4"
```
