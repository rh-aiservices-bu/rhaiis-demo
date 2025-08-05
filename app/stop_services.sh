#!/bin/bash

# Script to stop all demo services

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_info "Stopping Red Hat AI Agent Demo services..."

# Stop Streamlit
if tmux has-session -t streamlit-demo 2>/dev/null; then
    log_info "Stopping Streamlit application..."
    tmux kill-session -t streamlit-demo
    log_success "Streamlit stopped"
else
    log_warning "Streamlit session not found"
fi

# Stop vLLM
if tmux has-session -t vllm-demo 2>/dev/null; then
    log_info "Stopping vLLM server..."
    tmux kill-session -t vllm-demo
    log_success "vLLM session stopped"
else
    log_warning "vLLM session not found"
fi

# Stop vLLM container if still running
if podman ps --format "{{.Names}}" | grep -q "^vllm-demo$"; then
    log_info "Stopping vLLM container..."
    podman stop vllm-demo
    log_success "vLLM container stopped"
fi

# Stop PostgreSQL container
if podman ps --format "{{.Names}}" | grep -q "^postgres-demo$"; then
    log_info "Stopping PostgreSQL container..."
    podman stop postgres-demo
    log_success "PostgreSQL container stopped"
else
    log_warning "PostgreSQL container not found"
fi

# Clean up containers
log_info "Cleaning up containers..."
podman rm vllm-demo 2>/dev/null || true
podman rm postgres-demo 2>/dev/null || true

log_success "All services stopped successfully!"

# Show status
echo
echo "Service Status:"
echo "=============="

# Check ports
services_running=false

if nc -z localhost 8501 2>/dev/null; then
    echo "🔴 Streamlit (8501): Still running"
    services_running=true
else
    echo "🟢 Streamlit (8501): Stopped"
fi

if nc -z localhost 8000 2>/dev/null; then
    echo "🔴 vLLM (8000): Still running"
    services_running=true
else
    echo "🟢 vLLM (8000): Stopped"
fi

if nc -z localhost 5432 2>/dev/null; then
    echo "🔴 PostgreSQL (5432): Still running"
    services_running=true
else
    echo "🟢 PostgreSQL (5432): Stopped"
fi

if [ "$services_running" = true ]; then
    echo
    log_warning "Some services may still be running. Check manually if needed."
    echo "Active tmux sessions:"
    tmux list-sessions 2>/dev/null || echo "  No tmux sessions"
    echo
    echo "Running containers:"
    podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
else
    echo
    log_success "All demo services are completely stopped."
fi
