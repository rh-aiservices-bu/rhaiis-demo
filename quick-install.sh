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

# Install NVIDIA drivers via RPM Fusion (tested working method)
echo "🎮 Installing NVIDIA GPU drivers..."
echo "   - Installing EPEL and RPM Fusion repositories..."
sudo dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-10.noarch.rpm
sudo dnf install -y https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-$(rpm -E %rhel).noarch.rpm
sudo dnf install -y https://mirrors.rpmfusion.org/nonfree/el/rpmfusion-nonfree-release-$(rpm -E %rhel).noarch.rpm

echo "   - Installing kernel development packages..."
sudo dnf install -y kernel-devel kernel-headers dkms gcc make

echo "   - Installing NVIDIA drivers from RPM Fusion..."
sudo dnf install -y akmod-nvidia xorg-x11-drv-nvidia-cuda

# Install NVIDIA Container Toolkit
echo "🐳 Installing NVIDIA Container Toolkit..."
curl -s -L https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo | \
  sudo tee /etc/yum.repos.d/nvidia-container-toolkit.repo
sudo dnf install -y --nogpgcheck nvidia-container-toolkit

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
