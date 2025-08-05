#!/bin/bash

# Red Hat AI Agent Demo - Main Deployment Script
# This script sets up the complete demo environment on RHEL

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEMO_DIR="$HOME/rhaiis-demo"
VLLM_PORT=8000
STREAMLIT_PORT=8501
DB_PORT=5432
MODEL_NAME="ibm-granite/granite-3.3-2b-instruct"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 is not installed or not in PATH"
        return 1
    fi
    return 0
}

wait_for_service() {
    local service_name=$1
    local host=$2
    local port=$3
    local max_attempts=30
    local attempt=1
    
    log_info "Waiting for $service_name to start on $host:$port..."
    
    while [ $attempt -le $max_attempts ]; do
        if nc -z $host $port 2>/dev/null; then
            log_success "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    log_error "$service_name failed to start within $((max_attempts * 2)) seconds"
    return 1
}

# Main deployment function
main() {
    log_info "Starting Red Hat AI Agent Demo deployment..."
    
    # Check prerequisites
    log_info "Checking prerequisites..."
    
    if ! check_command "podman"; then
        log_error "Podman is required but not installed"
        exit 1
    fi
    
    if ! check_command "python3"; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    if ! check_command "pip3"; then
        log_error "pip3 is required but not installed"
        exit 1
    fi
    
    # Check for GPU access
    if ! podman run --rm --device nvidia.com/gpu=all docker.io/nvidia/cuda:11.0.3-base-ubuntu20.04 nvidia-smi &>/dev/null; then
        log_warning "GPU access test failed. vLLM may not work properly."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        log_success "GPU access confirmed"
    fi
    
    # Create demo directory if it doesn't exist
    if [ ! -d "$DEMO_DIR" ]; then
        log_info "Creating demo directory: $DEMO_DIR"
        mkdir -p "$DEMO_DIR"
    fi
    
    cd "$DEMO_DIR"
    
    # Step 1: Set up database
    log_info "Step 1: Setting up PostgreSQL database..."
    ./app/setup_database.sh
    
    if ! wait_for_service "PostgreSQL" "localhost" $DB_PORT; then
        log_error "Database setup failed"
        exit 1
    fi
    
    # Step 2: Install Python dependencies
    log_info "Step 2: Installing Python dependencies..."
    pip3 install --user streamlit psycopg2-binary requests
    
    # Step 3: Set up vLLM
    log_info "Step 3: Setting up vLLM server..."
    
    # Check if Hugging Face token is set
    if [ -z "$HUGGING_FACE_HUB_TOKEN" ]; then
        log_warning "HUGGING_FACE_HUB_TOKEN is not set"
        read -p "Enter your Hugging Face token: " -s hf_token
        echo
        export HUGGING_FACE_HUB_TOKEN="$hf_token"
    fi
    
    ./app/setup_vllm.sh
    
    if ! wait_for_service "vLLM" "localhost" $VLLM_PORT; then
        log_error "vLLM setup failed"
        exit 1
    fi
    
    # Step 4: Test vLLM connection
    log_info "Step 4: Testing vLLM connection..."
    if curl -s "http://localhost:$VLLM_PORT/v1/models" | grep -q "object"; then
        log_success "vLLM is responding correctly"
    else
        log_error "vLLM is not responding properly"
        exit 1
    fi
    
    # Step 5: Start Streamlit app
    log_info "Step 5: Starting Streamlit application..."
    ./app/setup_streamlit.sh
    
    if ! wait_for_service "Streamlit" "localhost" $STREAMLIT_PORT; then
        log_error "Streamlit setup failed"
        exit 1
    fi
    
    # Final status check
    log_info "Performing final status check..."
    
    # Check all services
    services_ok=true
    
    if ! nc -z localhost $DB_PORT; then
        log_error "PostgreSQL is not running on port $DB_PORT"
        services_ok=false
    fi
    
    if ! nc -z localhost $VLLM_PORT; then
        log_error "vLLM is not running on port $VLLM_PORT"
        services_ok=false
    fi
    
    if ! nc -z localhost $STREAMLIT_PORT; then
        log_error "Streamlit is not running on port $STREAMLIT_PORT"
        services_ok=false
    fi
    
    if [ "$services_ok" = true ]; then
        log_success "All services are running successfully!"
        echo
        echo "============================================"
        echo "🎉 Red Hat AI Agent Demo is ready!"
        echo "============================================"
        echo
        echo "Services running:"
        echo "  📊 Streamlit UI:    http://$(hostname -I | awk '{print $1}'):$STREAMLIT_PORT"
        echo "  🤖 vLLM Server:     http://localhost:$VLLM_PORT"
        echo "  🗄️  PostgreSQL:      localhost:$DB_PORT"
        echo
        echo "To access the demo:"
        echo "  1. Open your browser"
        echo "  2. Go to: http://$(hostname -I | awk '{print $1}'):$STREAMLIT_PORT"
        echo "  3. Try the sample prompts or ask your own questions"
        echo
        echo "To view logs:"
        echo "  tmux list-sessions"
        echo "  tmux attach-session -t <session-name>"
        echo
        echo "To stop all services:"
        echo "  ./app/stop_services.sh"
        echo
    else
        log_error "Some services failed to start. Check the logs for details."
        exit 1
    fi
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    log_error "Do not run this script as root. Run as a regular user with sudo access."
    exit 1
fi

# Run main function
main "$@"
