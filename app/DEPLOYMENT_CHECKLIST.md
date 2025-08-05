# RHAIIS Demo Deployment Checklist

## Pre-Deployment Checklist

### ✅ System Requirements
- [ ] **Hardware**: AWS g4dn.2xlarge or equivalent (8+ vCPUs, 32GB+ RAM)
- [ ] **GPU**: NVIDIA T4, A10G, or better with 6GB+ VRAM
- [ ] **Storage**: 200GB+ available disk space
- [ ] **OS**: RHEL 9.x, Rocky Linux 9.x, or CentOS Stream 9
- [ ] **Network**: Internet access for package downloads

### ✅ Account Requirements  
- [ ] **Red Hat Developer Account**: [Create free account](https://developers.redhat.com/)
- [ ] **AWS Account**: For EC2 instance provisioning
- [ ] **GitHub Account**: For repository access (optional)

### ✅ Initial System Setup
```bash
# Verify system
cat /etc/os-release
free -h
df -h
nproc
```

## Installation Steps

### Step 1: System Preparation
- [ ] **Update packages**: `sudo dnf update -y`
- [ ] **Install basics**: `sudo dnf install -y git tmux wget curl python3 python3-pip podman`
- [ ] **Verify Python**: `python3 --version` (should be 3.8+)
- [ ] **Verify pip**: `pip3 --version`

### Step 2: NVIDIA GPU Setup
- [ ] **Add NVIDIA repo**: 
  ```bash
  sudo dnf config-manager --add-repo https://developer.download.nvidia.com/compute/cuda/repos/rhel9/x86_64/cuda-rhel9.repo
  ```
- [ ] **Import GPG key**: 
  ```bash
  sudo rpm --import https://developer.download.nvidia.com/compute/cuda/repos/rhel9/x86_64/D42D0685.pub || true
  ```
- [ ] **Install drivers**: 
  ```bash
  sudo dnf install -y --nogpgcheck nvidia-driver nvidia-dkms cuda-drivers
  ```
- [ ] **Install container toolkit**: 
  ```bash
  curl -s -L https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo | \
    sudo tee /etc/yum.repos.d/nvidia-container-toolkit.repo
  sudo dnf install -y --nogpgcheck nvidia-container-toolkit
  ```
- [ ] **Configure podman**: 
  ```bash
  sudo nvidia-ctk runtime configure --runtime=podman --config=/usr/share/containers/containers.conf
  ```
- [ ] **REBOOT SYSTEM**: `sudo reboot`

### Step 3: Post-Reboot Verification
- [ ] **Check GPU**: `nvidia-smi` (should show GPU info)
- [ ] **Generate CDI specs**: `sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml`
- [ ] **Test GPU in container**: 
  ```bash
  sudo podman run --rm --device nvidia.com/gpu=all nvidia/cuda:12.0-base-ubuntu20.04 nvidia-smi
  ```

### Step 4: Container Registry Authentication
- [ ] **Login to Red Hat registry**: 
  ```bash
  sudo podman login registry.redhat.io
  # Enter Red Hat Developer credentials
  ```
- [ ] **Verify login**: `sudo podman search registry.redhat.io/ubi9`

### Step 5: Demo Deployment
- [ ] **Clone repository**: 
  ```bash
  git clone https://github.com/YOUR_USERNAME/rhaiis-demo.git
  cd rhaiis-demo/app
  ```
- [ ] **Run deployment**: `./deploy.sh`
- [ ] **Wait for completion** (5-10 minutes for first run)

## Post-Deployment Verification

### ✅ Service Status Checks
- [ ] **PostgreSQL container**: `sudo podman ps | grep crm-postgres`
- [ ] **Flask process**: `ps aux | grep python.*app.py`
- [ ] **Port availability**: `netstat -tlnp | grep -E "(5000|5432)"`

### ✅ API Endpoint Tests
- [ ] **Health check**: 
  ```bash
  curl -X GET "http://localhost:5000/health"
  # Expected: {"status":"AI Agent Service is running"}
  ```
- [ ] **Database access**: 
  ```bash
  curl -X GET "http://localhost:5000/db/sales"
  # Expected: JSON with sales data
  ```
- [ ] **AI chat test**: 
  ```bash
  curl -X POST "http://localhost:5000/agent/chat" \
       -H "Content-Type: application/json" \
       -d '{"message": "Hello, are you working?"}'
  # Expected: AI response with status success
  ```

### ✅ Comprehensive Testing
- [ ] **Run test suite**: `./test_api.sh`
- [ ] **Check all endpoints respond**: Health, Sales, Accounts, Support, Chat
- [ ] **Verify AI responses are intelligent**: Ask business questions

## Performance Validation

### ✅ Resource Usage
- [ ] **GPU utilization**: `nvidia-smi` (should show model loaded)
- [ ] **Memory usage**: `free -h` (should have headroom)
- [ ] **Disk space**: `df -h` (should have space remaining)
- [ ] **Response times**: API calls should respond within 5-10 seconds

### ✅ Load Testing (Optional)
- [ ] **Multiple concurrent requests**: Test with several simultaneous API calls
- [ ] **Long-running queries**: Test complex business intelligence questions
- [ ] **Database stress test**: Run multiple database queries simultaneously

## Troubleshooting Checklist

### ❌ Common Issues
- [ ] **GPU not detected**: 
  - Check `nvidia-smi` output
  - Verify reboot after driver installation
  - Ensure correct EC2 instance type (g4dn.*)
  
- [ ] **Container auth failures**: 
  - Verify Red Hat Developer account active
  - Re-run `sudo podman login registry.redhat.io`
  
- [ ] **Port conflicts**: 
  - Check for existing services on ports 5000/5432
  - Kill conflicting processes: `sudo fuser -k 5000/tcp`
  
- [ ] **Out of memory**: 
  - Verify sufficient RAM (16GB+ recommended)
  - Add swap space if needed
  - Monitor with `htop`
  
- [ ] **Model loading failures**: 
  - Check internet connectivity
  - Verify disk space (need 10GB+ for model)
  - Clear cache: `rm -rf ~/.cache/huggingface`

### ❌ Recovery Procedures
- [ ] **Complete reset**: 
  ```bash
  ./stop_services.sh
  sudo podman system prune -a
  rm -rf ~/.cache/huggingface
  ./deploy.sh
  ```
- [ ] **Database reset**: 
  ```bash
  sudo podman stop crm-postgres
  sudo podman rm crm-postgres
  ./setup_database.sh
  ```

## Success Criteria

### ✅ Deployment Success
- [ ] All API endpoints responding correctly
- [ ] AI agent providing intelligent responses
- [ ] Database queries returning expected data
- [ ] GPU acceleration working (check nvidia-smi)
- [ ] No critical errors in logs
- [ ] Response times under 10 seconds

### ✅ Demo Readiness
- [ ] Can demonstrate CRM business intelligence queries
- [ ] AI provides actionable insights from database
- [ ] Multiple query types work (sales, accounts, support)
- [ ] System stable under normal usage
- [ ] Documentation complete and accessible

## Maintenance Tasks

### 🔄 Regular Maintenance
- [ ] **Monitor logs**: Check `flask.log` for errors
- [ ] **Monitor resources**: Use `nvidia-smi`, `htop`, `df -h`
- [ ] **Update dependencies**: Periodic `pip3 install --upgrade`
- [ ] **Database maintenance**: Monitor PostgreSQL container health
- [ ] **Security updates**: Regular `sudo dnf update`

### 🔄 Backup Procedures
- [ ] **Database backup**: Export PostgreSQL data if needed
- [ ] **Configuration backup**: Save modified config files
- [ ] **Model cache**: Preserve downloaded models to avoid re-download

## Final Validation

- [ ] **Complete demo walkthrough**: End-to-end demonstration working
- [ ] **Documentation review**: All docs accurate and complete
- [ ] **Performance acceptable**: Response times meet requirements
- [ ] **Stable operation**: No crashes or errors over extended use
- [ ] **Resource utilization reasonable**: Not exceeding system capacity

---

**Deployment Status**: [ ] ✅ COMPLETE / [ ] ❌ ISSUES FOUND

**Notes**: ___________________________________

**Deployment Date**: _______________

**Deployed by**: ___________________
