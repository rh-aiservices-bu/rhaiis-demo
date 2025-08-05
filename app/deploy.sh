#!/bin/bash

set -e

echo "=========================================="
echo "   Red Hat AI Inference Server Demo"
echo "   Flask API with Granite Agent"
echo "=========================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "[ERROR] This script should not be run as root"
   exit 1
fi

# Install Python dependencies
echo "[INFO] Installing Python dependencies..."
pip3 install --user -r requirements.txt

# Set up database
echo "[INFO] Setting up PostgreSQL database..."
./setup_database.sh

# Set up vLLM server
echo "[INFO] Setting up vLLM server..."
./setup_vllm.sh

# Wait for services to be ready
echo "[INFO] Waiting for services to be ready..."
echo "[INFO] Waiting for PostgreSQL..."
sleep 15

echo "[INFO] Waiting for vLLM to load model (this may take several minutes)..."
for i in {1..60}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "[SUCCESS] vLLM service is ready!"
        break
    fi
    echo "[INFO] Waiting for vLLM... ($i/60)"
    sleep 10
done

# Check if vLLM is ready
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "[WARNING] vLLM service may still be loading. You can start the Flask app anyway."
    echo "[INFO] Monitor vLLM logs with: sudo podman logs -f granite-vllm"
fi

echo ""
echo "=========================================="
echo "   Setup Complete!"
echo "=========================================="
echo ""
echo "Services running:"
echo "  • PostgreSQL: localhost:5432"
echo "  • vLLM API: localhost:8000"
echo ""
echo "To start the Flask API:"
echo "  python3 app.py"
echo ""
echo "Then test with:"
echo "  curl http://localhost:5000/health"
echo ""
echo "=========================================="
