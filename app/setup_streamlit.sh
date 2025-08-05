#!/bin/bash

# Script to setup and start the Streamlit application

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

# Configuration
STREAMLIT_PORT=8501
VLLM_ENDPOINT="localhost:8000"
MODEL_NAME="ibm-granite/granite-3.3-2b-instruct"

# Set environment variables for the Streamlit app
export VLLM_ENDPOINT="$VLLM_ENDPOINT"
export MODEL_NAME="$MODEL_NAME"
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_NAME="claimdb"
export DB_USER="claimdb"
export DB_PASSWORD="claimdb"

log_info "Setting up Streamlit environment..."

# Check if Python dependencies are installed
log_info "Checking Python dependencies..."

python3 -c "import streamlit, psycopg2, requests" 2>/dev/null
if [ $? -ne 0 ]; then
    log_warning "Some Python dependencies are missing. Installing..."
    pip3 install --user streamlit psycopg2-binary requests
    
    if [ $? -ne 0 ]; then
        log_error "Failed to install Python dependencies"
        exit 1
    fi
    log_success "Python dependencies installed"
else
    log_success "Python dependencies are already installed"
fi

# Check if Streamlit session already exists and kill it
if tmux has-session -t streamlit-demo 2>/dev/null; then
    log_info "Stopping existing Streamlit session..."
    tmux kill-session -t streamlit-demo 2>/dev/null || true
fi

# Start Streamlit in a tmux session
log_info "Starting Streamlit application on port $STREAMLIT_PORT..."

# Create tmux session for Streamlit
tmux new-session -d -s streamlit-demo

# Navigate to the app directory and start Streamlit
tmux send-keys -t streamlit-demo "cd $HOME/rhaiis-demo" Enter
tmux send-keys -t streamlit-demo "export VLLM_ENDPOINT=$VLLM_ENDPOINT" Enter
tmux send-keys -t streamlit-demo "export MODEL_NAME='$MODEL_NAME'" Enter
tmux send-keys -t streamlit-demo "export DB_HOST=$DB_HOST" Enter
tmux send-keys -t streamlit-demo "export DB_PORT=$DB_PORT" Enter
tmux send-keys -t streamlit-demo "export DB_NAME=$DB_NAME" Enter
tmux send-keys -t streamlit-demo "export DB_USER=$DB_USER" Enter
tmux send-keys -t streamlit-demo "export DB_PASSWORD=$DB_PASSWORD" Enter

# Start Streamlit
tmux send-keys -t streamlit-demo "python3 -m streamlit run app/streamlit_app.py --server.port $STREAMLIT_PORT --server.address 0.0.0.0 --server.headless true" Enter

log_success "Streamlit application started in tmux session 'streamlit-demo'"
log_info "Monitor with: tmux attach-session -t streamlit-demo"
log_info "Access at: http://$(hostname -I | awk '{print $1}'):$STREAMLIT_PORT"

# Wait a moment for Streamlit to start
sleep 3

# Verify Streamlit is running by checking tmux session
if tmux has-session -t streamlit-demo 2>/dev/null; then
    log_success "Streamlit session is active"
else
    log_error "Streamlit session failed to start"
    exit 1
fi
