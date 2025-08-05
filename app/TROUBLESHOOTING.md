# RHAIIS Demo Troubleshooting Guide

## Pre-Installation Issues

### 1. NVIDIA Driver Installation Failures

**Problem**: GPG key errors during NVIDIA driver installation
```bash
# Solution: Install with GPG check bypass
sudo dnf install -y --nogpgcheck nvidia-driver nvidia-dkms cuda-drivers
```

**Problem**: Driver compilation fails
```bash
# Solution: Install kernel headers and development tools
sudo dnf install -y kernel-devel kernel-headers gcc make dkms
sudo dnf groupinstall -y "Development Tools"
```

**Problem**: Reboot required but not performed
```bash
# Solution: Always reboot after driver installation
sudo reboot
```

### 2. Container Runtime Issues

**Problem**: Podman not available
```bash
# Solution: Install podman
sudo dnf install -y podman podman-docker
```

**Problem**: Container registry authentication fails
```bash
# Solution: Login to Red Hat registry
sudo podman login registry.redhat.io
# Enter Red Hat Developer account credentials
```

### 3. Python Environment Issues

**Problem**: pip3 not found
```bash
# Solution: Install Python pip
sudo dnf install -y python3-pip python3-devel
```

**Problem**: Permission issues with pip install
```bash
# Solution: Use --user flag
pip3 install --user -r requirements.txt
```

## Deployment Issues

### 1. Database Connection Problems

**Problem**: PostgreSQL container fails to start
```bash
# Check container status
sudo podman ps -a

# View container logs  
sudo podman logs crm-postgres

# Remove and recreate if needed
sudo podman stop crm-postgres
sudo podman rm crm-postgres
./setup_database.sh
```

**Problem**: Port 5432 already in use
```bash
# Find process using port
sudo netstat -tlnp | grep 5432

# Kill conflicting process
sudo fuser -k 5432/tcp

# Restart database
./setup_database.sh
```

### 2. AI Model Loading Issues

**Problem**: Model download fails
```bash
# Check internet connectivity
curl -I https://huggingface.co

# Check disk space (need 10GB+ free)
df -h

# Clear cache and retry
rm -rf ~/.cache/huggingface
python3 app.py
```

**Problem**: CUDA out of memory
```bash
# Check GPU memory
nvidia-smi

# Restart with CPU fallback
export CUDA_VISIBLE_DEVICES=""
python3 app.py
```

**Problem**: Model loading takes too long
```bash
# Monitor progress in logs
tail -f flask.log

# First-time download can take 5-10 minutes
# Subsequent starts should be under 2 minutes
```

### 3. Flask Application Issues

**Problem**: Flask app won't start
```bash
# Check Python version (need 3.8+)
python3 --version

# Check dependencies
pip3 list | grep flask

# View detailed error logs
cat flask.log
```

**Problem**: Port 5000 conflicts
```bash
# Find process using port 5000
sudo netstat -tlnp | grep 5000

# Kill conflicting process
sudo fuser -k 5000/tcp

# Restart Flask app
python3 app.py
```

## Runtime Issues

### 1. API Response Problems

**Problem**: Health check fails
```bash
# Test API endpoint
curl -v http://localhost:5000/health

# Check Flask process
ps aux | grep python.*app.py

# Restart if needed
./stop_services.sh
./deploy.sh
```

**Problem**: AI chat returns errors
```bash
# Check if model is loaded
grep "Model loaded successfully" flask.log

# Test with simple query
curl -X POST "http://localhost:5000/agent/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello"}'
```

**Problem**: Database queries fail
```bash
# Test database connection
curl http://localhost:5000/db/sales

# Check PostgreSQL container
sudo podman ps | grep postgres

# Restart database if needed  
sudo podman restart crm-postgres
```

### 2. Performance Issues

**Problem**: Slow AI responses
```bash
# Check GPU usage
nvidia-smi

# Monitor system resources
htop

# Consider using smaller model or CPU fallback
```

**Problem**: High memory usage
```bash
# Check memory consumption
free -h

# Restart services to clear memory
./stop_services.sh
./deploy.sh
```

## System Resource Issues

### 1. Insufficient Disk Space

**Problem**: No space left on device
```bash
# Check disk usage
df -h

# Clean up Docker/Podman images
sudo podman system prune -a

# Clear Python cache
rm -rf ~/.cache/pip ~/.cache/huggingface

# Remove old logs
rm -f *.log
```

### 2. Memory Issues

**Problem**: System runs out of memory
```bash
# Check memory usage
free -h

# Kill unnecessary processes
sudo pkill -f jupyter
sudo pkill -f code-server

# Add swap space if needed
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 3. GPU Issues

**Problem**: GPU not detected after reboot
```bash
# Reload NVIDIA modules
sudo modprobe nvidia

# Check driver status
lsmod | grep nvidia

# Reinstall if needed
sudo dnf reinstall -y nvidia-driver
```

**Problem**: GPU memory errors
```bash
# Check GPU processes
nvidia-smi

# Kill GPU processes
sudo fuser -v /dev/nvidia*
sudo pkill -f python

# Restart services
./deploy.sh
```

## Network Issues

### 1. API Access Problems

**Problem**: Cannot access API from outside
```bash
# Check if Flask binds to all interfaces
netstat -tlnp | grep 5000

# Ensure firewall allows access
sudo firewall-cmd --add-port=5000/tcp --permanent
sudo firewall-cmd --reload
```

**Problem**: Container networking issues
```bash
# Check podman network
sudo podman network ls

# Restart networking
sudo systemctl restart podman
```

## Debug Commands

### System Information
```bash
# OS version
cat /etc/os-release

# GPU information
nvidia-smi
lspci | grep -i nvidia

# Memory and CPU
free -h
nproc
```

### Service Status
```bash
# Check all processes
ps aux | grep -E "(python|postgres)"

# Check containers
sudo podman ps -a

# Check ports
netstat -tlnp | grep -E "(5000|5432)"
```

### Log Analysis
```bash
# Flask application logs
tail -f flask.log

# PostgreSQL logs
sudo podman logs crm-postgres

# System logs
journalctl -u podman --since "1 hour ago"
```

### Resource Monitoring
```bash
# Real-time system monitoring
htop

# GPU monitoring
watch -n 1 nvidia-smi

# Disk I/O monitoring
iotop
```

## Recovery Procedures

### Complete Reset
```bash
# Stop all services
./stop_services.sh

# Remove all containers
sudo podman stop --all
sudo podman rm --all

# Clear caches
rm -rf ~/.cache/huggingface ~/.cache/pip
rm -f *.log *.pid

# Redeploy
./deploy.sh
```

### Database Reset
```bash
# Remove database container
sudo podman stop crm-postgres
sudo podman rm crm-postgres

# Recreate database
./setup_database.sh
```

### Model Cache Reset
```bash
# Clear model cache
rm -rf ~/.cache/huggingface

# Restart Flask app (will re-download model)
pkill -f python.*app.py
python3 app.py
```

## Getting Help

1. **Check Logs First**: Always examine `flask.log` and container logs
2. **Verify Prerequisites**: Ensure all system requirements are met
3. **Resource Check**: Confirm adequate CPU, RAM, GPU, and disk space
4. **Network Connectivity**: Test internet access for model downloads
5. **Clean Installation**: Try complete reset if issues persist

## Common Solutions Summary

| Issue | Quick Fix |
|-------|-----------|
| GPU not detected | `sudo reboot` after driver install |
| Port conflicts | `sudo fuser -k 5000/tcp` |
| Out of memory | Restart services or add swap |
| Model won't load | Check disk space and clear cache |
| Database connection fails | Restart PostgreSQL container |
| Permission errors | Use `--user` flag with pip |
| Container auth fails | Login to registry.redhat.io |
