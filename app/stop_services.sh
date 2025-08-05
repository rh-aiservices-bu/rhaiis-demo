#!/bin/bash

echo "[INFO] Stopping all demo services..."

# Stop Flask app (if running in background)
pkill -f "python3 app.py" 2>/dev/null || true

# Stop containers
echo "[INFO] Stopping PostgreSQL container..."
sudo podman stop crm-postgres 2>/dev/null || true
sudo podman rm crm-postgres 2>/dev/null || true

echo "[INFO] Stopping vLLM container..."
sudo podman stop granite-vllm 2>/dev/null || true
sudo podman rm granite-vllm 2>/dev/null || true

echo "[SUCCESS] All services stopped and containers removed"
