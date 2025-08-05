#!/bin/bash

# Stop all RHAIIS demo services
echo "Stopping RHAIIS CRM Demo services..."

# Stop Flask app
if [ -f flask.pid ]; then
    PID=$(cat flask.pid)
    if kill -0 $PID 2>/dev/null; then
        echo "Stopping Flask app (PID: $PID)..."
        kill $PID
        rm flask.pid
    fi
fi

# Stop vLLM server
if [ -f vllm.pid ]; then
    PID=$(cat vllm.pid)
    if kill -0 $PID 2>/dev/null; then
        echo "Stopping vLLM server (PID: $PID)..."
        kill $PID
        rm vllm.pid
    fi
fi

# Stop and remove PostgreSQL container
echo "Stopping PostgreSQL container..."
sudo podman stop crm-postgres 2>/dev/null || true
sudo podman rm crm-postgres 2>/dev/null || true

# Kill any remaining processes
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "vllm.entrypoints" 2>/dev/null || true

echo "All services stopped."
