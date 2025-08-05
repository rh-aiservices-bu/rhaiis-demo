#!/bin/bash

# RHAIIS Demo Quick Installation Script
# Run this on a fresh RHEL 10.x system with GPU

set -e

echo "=========================================="
echo "  RHAIIS Demo Quick Installation"
echo "=========================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    echo "❌ Do not run this script as root!"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
sudo dnf update -y

# Install basic tools
echo "🔧 Installing basic tools..."
sudo dnf install -y git tmux wget curl python3 python3-pip podman

# Install NVIDIA drivers
echo "🎮 Installing NVIDIA GPU drivers..."
sudo dnf config-manager --add-repo https://developer.download.nvidia.com/compute/cuda/repos/rhel10/x86_64/cuda-rhel10.repo
sudo rpm --import https://developer.download.nvidia.com/compute/cuda/repos/rhel10/x86_64/D42D0685.pub || true
sudo dnf install -y --nogpgcheck nvidia-driver nvidia-dkms cuda-drivers

# Install NVIDIA Container Toolkit
echo "🐳 Installing NVIDIA Container Toolkit..."
curl -s -L https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo | \
  sudo tee /etc/yum.repos.d/nvidia-container-toolkit.repo
sudo dnf install -y --nogpgcheck nvidia-container-toolkit

# Configure podman for NVIDIA
sudo nvidia-ctk runtime configure --runtime=podman --config=/usr/share/containers/containers.conf

echo ""
echo "✅ Installation completed!"
echo ""
echo "⚠️  REBOOT REQUIRED to load GPU drivers:"
echo "   sudo reboot"
echo ""
echo "After reboot, run:"
echo "   cd rhaiis-demo/app"
echo "   sudo podman login registry.redhat.io"
echo "   ./deploy.sh"
echo ""
