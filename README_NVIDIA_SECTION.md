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
