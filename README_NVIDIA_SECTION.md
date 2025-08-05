# NVIDIA Driver Installation for RHEL 10

This document provides detailed instructions for installing NVIDIA GPU drivers on Red Hat Enterprise Linux 10, specifically tested for the RHAIIS demo.

## Overview

The RHAIIS demo requires NVIDIA GPU drivers for accelerated AI inference. After extensive testing, we've found that **RPM Fusion repositories** provide the most reliable installation method for RHEL 10.

## Tested Working Method: RPM Fusion

### Why RPM Fusion?

- **Reliability**: Precompiled packages that work with RHEL 10
- **Automatic Updates**: Drivers update with system updates
- **Kernel Compatibility**: Automatic kernel module building via DKMS
- **No Manual Compilation**: Avoids common build issues

### Prerequisites

1. Fresh RHEL 10.x system
2. NVIDIA GPU (tested with Tesla T4, A10G)
3. Internet connection
4. Non-root user with sudo privileges

### Step-by-Step Installation

#### 1. Install EPEL Repository
```bash
sudo dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-10.noarch.rpm
```

#### 2. Install RPM Fusion Repositories
```bash
# Free repository
sudo dnf install -y https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-$(rpm -E %rhel).noarch.rpm

# Non-free repository (required for NVIDIA drivers)
sudo dnf install -y https://mirrors.rpmfusion.org/nonfree/el/rpmfusion-nonfree-release-$(rpm -E %rhel).noarch.rpm
```

#### 3. Install Kernel Development Tools
```bash
sudo dnf install -y kernel-devel kernel-headers dkms gcc make
```

#### 4. Install NVIDIA Drivers
```bash
sudo dnf install -y akmod-nvidia xorg-x11-drv-nvidia-cuda
```

#### 5. Reboot System
```bash
sudo reboot
```

#### 6. Verify Installation
After reboot:
```bash
nvidia-smi
```

Expected output should show your GPU information and driver version.

### Package Details

- **`akmod-nvidia`**: Automatically builds NVIDIA kernel modules for your kernel
- **`xorg-x11-drv-nvidia-cuda`**: CUDA support for compute workloads
- **DKMS**: Automatically rebuilds drivers when kernel updates

## Container Support

For containerized GPU workloads (required for vLLM):

### Install NVIDIA Container Toolkit
```bash
curl -s -L https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo | \
  sudo tee /etc/yum.repos.d/nvidia-container-toolkit.repo
sudo dnf install -y --nogpgcheck nvidia-container-toolkit
```

### Test Container GPU Access
```bash
sudo podman run --rm --gpus all nvidia/cuda:12.0-base-ubuntu20.04 nvidia-smi
```

## Alternative Methods (Not Recommended for RHEL 10)

### NVIDIA CUDA Repository Method
❌ **Issues Found:**
- CUDA repository for RHEL 10 returns 404 errors
- Package conflicts with system packages
- Incomplete dependency resolution

### NVIDIA Runfile Installer
❌ **Issues Found:**
- Kernel/compiler version mismatches
- Complex manual configuration required
- Doesn't integrate with package management

### Native RHEL Packages
❌ **Issues Found:**
- NVIDIA drivers not available in standard RHEL 10 repositories
- Would require RHEL subscription with additional channels

## Troubleshooting

### Common Issues and Solutions

#### 1. "akmod-nvidia" Package Not Found
**Cause**: RPM Fusion repositories not properly installed

**Solution**:
```bash
# Verify repositories are enabled
sudo dnf repolist | grep rpmfusion

# If missing, reinstall RPM Fusion
sudo dnf install -y https://mirrors.rpmfusion.org/nonfree/el/rpmfusion-nonfree-release-$(rpm -E %rhel).noarch.rpm
```

#### 2. Kernel Module Build Failures
**Cause**: Missing kernel headers or development tools

**Solution**:
```bash
# Ensure kernel versions match
uname -r
rpm -q kernel-devel kernel-headers

# Reinstall if versions don't match
sudo dnf install -y kernel-devel-$(uname -r) kernel-headers-$(uname -r)
```

#### 3. "nvidia-smi" Not Found After Reboot
**Cause**: Driver installation incomplete or kernel module not loaded

**Solution**:
```bash
# Check if NVIDIA modules are loaded
lsmod | grep nvidia

# Check akmods service status
sudo systemctl status akmods

# Manually trigger module build
sudo akmods --force
sudo reboot
```

#### 4. Container GPU Access Denied
**Cause**: NVIDIA Container Toolkit not properly configured

**Solution**:
```bash
# Verify container toolkit installation
nvidia-ctk --version

# Test basic GPU access
sudo podman run --rm --device nvidia.com/gpu=all nvidia/cuda:12.0-base-ubuntu20.04 nvidia-smi
```

### Verification Commands

#### System-Level Verification
```bash
# Check driver version
nvidia-smi

# Check loaded modules
lsmod | grep nvidia

# Check hardware detection
lspci | grep -i nvidia

# Check CUDA version
nvcc --version  # If CUDA toolkit installed
```

#### Container-Level Verification
```bash
# Test basic container GPU access
sudo podman run --rm --gpus all nvidia/cuda:12.0-base-ubuntu20.04 nvidia-smi

# Test with PyTorch (if needed)
sudo podman run --rm --gpus all pytorch/pytorch:latest python -c "import torch; print(torch.cuda.is_available())"
```

## Performance Tuning

### GPU Persistence Mode
Enable persistence mode for better performance:
```bash
sudo nvidia-smi -pm 1
```

### Power Management
Set maximum power limit (adjust based on your GPU):
```bash
sudo nvidia-smi -pl 300  # Set to 300W, adjust as needed
```

## Integration with RHAIIS Demo

The RHAIIS demo requires:
1. NVIDIA drivers (installed via this guide)
2. NVIDIA Container Toolkit (for podman GPU access)
3. Sufficient GPU memory (8GB+ recommended for Granite model)

After following this guide, the demo's `./deploy.sh` script should successfully:
- Launch vLLM server with GPU acceleration
- Load the Granite model with CUDA support
- Provide high-performance AI inference

## Maintenance

### Automatic Updates
RPM Fusion drivers update automatically with system updates:
```bash
sudo dnf update
# Reboot if kernel was updated
```

### Manual Driver Updates
```bash
sudo dnf update akmod-nvidia xorg-x11-drv-nvidia-cuda
sudo reboot
```

### Kernel Updates
DKMS automatically rebuilds driver modules for new kernels. If issues occur:
```bash
sudo akmods --force
sudo reboot
```

## Support and Resources

- **RPM Fusion Documentation**: https://rpmfusion.org/
- **NVIDIA Developer Documentation**: https://developer.nvidia.com/
- **RHEL Documentation**: https://access.redhat.com/documentation/

For RHAIIS demo-specific issues, refer to the main [README.md](README.md) troubleshooting section.
