# Red Hat AI Inference - Linux CRM Demo

A demonstration of Red Hat AI Inference capabilities using IBM Granite models for CRM business intelligence and analytics on bare-metal Linux.

## Prerequisites

- **AWS EC2**: `g5.4xlarge` instance recommended
- **OS**: Red Hat Enterprise Linux 10
- **Storage**: 200GB+ EBS volume
- **Account**: Red Hat Developer account (free)

## Quick Start

### 1. Launch AWS Instance

Create a `g5.4xlarge` EC2 instance with:
- **AMI**: Red Hat Enterprise Linux 10
- **Storage**: 200GB GP3 EBS volume
- **Security Group**: Allow SSH (port 22) and HTTP (port 5000)

### 2. Clone and Setup

```bash
ssh -i your-key.pem ec2-user@your-instance-ip

git clone https://github.com/rh-aiservices-bu/rhaiis-demo.git
cd rhaiis-demo/linux

# Run the automated setup script (installs GPU drivers and dependencies)
./quick-install.sh

# Reboot to load GPU drivers
sudo reboot
```

### 3. Deploy

```bash
ssh -i your-key.pem ec2-user@your-instance-ip
cd rhaiis-demo/linux/app

# Authenticate with Red Hat registry
sudo podman login registry.redhat.io

# Deploy the complete demo
./deploy.sh
```

### 4. Verify

```bash
curl -X GET "http://localhost:5000/health"
./test_api.sh
```

## What This Demo Shows

An AI-powered CRM assistant that can:
- Analyze sales opportunities and revenue trends
- Assess customer account health and satisfaction metrics
- Process support case analytics and identify issues
- Provide actionable business intelligence insights
- Dynamically call database tools based on natural language queries

### Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Flask API     │◄──►│   Granite AI     │◄──►│   PostgreSQL    │
│   (Port 5000)   │    │   Agent (GPU)    │    │   CRM Database  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check |
| `/agent/chat` | POST | AI-powered chat interface |
| `/db/sales` | GET | Sales opportunities data |
| `/db/accounts` | GET | Customer accounts data |
| `/db/support` | GET | Support cases data |

## Example Usage

```bash
curl -X POST "http://localhost:5000/agent/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "What are our top sales opportunities by value?"}'
```

## GPU Drivers

See [NVIDIA Installation Guide](README_NVIDIA_SECTION.md) for detailed driver installation and troubleshooting.

## Service Management

```bash
./app/deploy.sh           # Start services
./app/stop_services.sh    # Stop services
```

## Troubleshooting

See [Troubleshooting Guide](app/TROUBLESHOOTING.md) for common issues.
