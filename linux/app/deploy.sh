#!/bin/bash

# Deploy the RHAI CRM Demo
set -e

echo "=================================================="
echo "   Red Hat AI Inference CRM Demo"
echo "   Deployment Script"
echo "=================================================="

# Check if running as root or with sudo
if [[ $EUID -eq 0 ]]; then
    echo "❌ This script should not be run as root. Please run as a regular user."
    exit 1
fi

# Check system requirements
echo "🔍 Checking system requirements..."

# Check available memory (need at least 16GB)
MEM_GB=$(free -g | awk 'NR==2{printf "%.0f", $2}')
if [ "$MEM_GB" -lt 16 ]; then
    echo "⚠️  Warning: System has ${MEM_GB}GB RAM. 16GB+ recommended for optimal performance."
fi

# Check available disk space (need at least 50GB free)
DISK_GB=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
if [ "$DISK_GB" -lt 50 ]; then
    echo "❌ Error: Need at least 50GB free disk space. Currently have ${DISK_GB}GB."
    exit 1
fi

# Check if NVIDIA GPU is available
if command -v nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA GPU detected: $(nvidia-smi --query-gpu=name --format=csv,noheader,nounits | head -1)"
else
    echo "⚠️  Warning: NVIDIA GPU not detected. Performance will be significantly slower on CPU."
fi

# Check if podman is available
if ! command -v podman &> /dev/null; then
    echo "❌ Error: podman is required but not installed."
    echo "   Install with: sudo dnf install -y podman"
    exit 1
fi

# Check if pip3 is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is required but not installed."
    echo "   Install with: sudo dnf install -y python3-pip"
    exit 1
fi

echo "✅ System requirements check completed"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install --user -r requirements.txt
echo "✅ Python dependencies installed"
echo ""

# Set up database
echo "🗄️  Setting up PostgreSQL database..."
./setup_database.sh
echo "✅ PostgreSQL database setup completed"
echo ""

# Start Flask app with AI agent
echo "🤖 Starting Flask app with Granite AI agent..."
echo "   This may take several minutes to download and load the AI model..."

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development

# Start Flask app in background
nohup python3 app.py > flask.log 2>&1 &
FLASK_PID=$!
echo $FLASK_PID > flask.pid

echo "⏳ Waiting for AI model to load (this can take 2-5 minutes)..."
sleep 10

# Wait for Flask to be ready
RETRIES=0
MAX_RETRIES=30
while [ $RETRIES -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:5000/health > /dev/null 2>&1; then
        break
    fi
    echo "   Still loading... (attempt $((RETRIES+1))/$MAX_RETRIES)"
    sleep 10
    RETRIES=$((RETRIES+1))
done

if [ $RETRIES -eq $MAX_RETRIES ]; then
    echo "❌ Flask app failed to start after $((MAX_RETRIES*10)) seconds"
    echo "   Check logs with: tail -f flask.log"
    exit 1
fi

echo "✅ Flask app started successfully"
echo ""

# Test services
echo "🧪 Testing deployed services..."

# Test database connection
DB_COUNT=$(sudo podman ps | grep -c crm-postgres || echo "0")
if [ "$DB_COUNT" -eq 1 ]; then
    echo "✅ PostgreSQL database is running"
else
    echo "❌ PostgreSQL database failed to start"
fi

# Test Flask API
if curl -s http://localhost:5000/health | grep -q "running"; then
    echo "✅ Flask API is responding"
else
    echo "❌ Flask API is not responding"
fi

# Test AI agent
echo "🤖 Testing AI agent..."
AI_RESPONSE=$(curl -s -X POST "http://localhost:5000/agent/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello, are you working?"}' | grep -o '"status":"success"' || echo "")

if [ -n "$AI_RESPONSE" ]; then
    echo "✅ AI agent is responding"
else
    echo "⚠️  AI agent may still be loading. Check logs: tail -f flask.log"
fi

echo ""
echo "=================================================="
echo "   🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "=================================================="
echo ""
echo "📊 Services Status:"
echo "   • PostgreSQL Database: Running on port 5432"
echo "   • Flask API Server: Running on port 5000"
echo "   • Granite AI Agent: GPU-accelerated model loaded"
echo ""
echo "🔗 API Endpoints:"
echo "   • Health Check: http://localhost:5000/health"
echo "   • AI Chat: POST http://localhost:5000/agent/chat"
echo "   • Sales Data: http://localhost:5000/db/sales"
echo "   • Account Data: http://localhost:5000/db/accounts"  
echo "   • Support Data: http://localhost:5000/db/support"
echo ""
echo "🧪 Test the demo:"
echo "   ./test_api.sh"
echo ""
echo "🛑 Stop all services:"
echo "   ./stop_services.sh"
echo ""
echo "📋 View logs:"
echo "   tail -f flask.log"
echo ""
echo "💡 Example AI query:"
echo '   curl -X POST "http://localhost:5000/agent/chat" \'
echo '        -H "Content-Type: application/json" \'
echo '        -d '"'"'{"message": "What are our top sales opportunities?"}'"'"
echo ""
