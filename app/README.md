# Red Hat AI Agent Demo - Simplified Version

This directory contains a simplified version of the Red Hat AI Agentic Demo that works directly with vLLM and Granite models, without requiring MCP (Model Context Protocol) or Llama Stack dependencies.

## Overview

The simplified demo provides the same core functionality as the original but with a much simpler architecture:

- **Direct vLLM Integration**: Communicates directly with Red Hat AI Inference Server (vLLM)
- **Native Tool Calling**: Implements tool calling using pattern matching instead of complex frameworks
- **PostgreSQL Database**: Uses the same database schema and sample data
- **Streamlit UI**: Maintains the same user experience with a web-based chat interface

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │───▶│  Granite Agent   │───▶│  vLLM Server    │
│   (Port 8501)   │    │  (Python Class)  │    │   (Port 8000)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  PostgreSQL DB  │
                       │   (Port 5432)   │
                       └─────────────────┘
```

## Files Description

### Core Application Files
- `agent.py` - Main agent class with tool calling capabilities
- `db_tools.py` - Database connection and CRM tools
- `streamlit_app.py` - Web UI application
- `simple_agentic_demo.py` - Basic command-line demo

### Deployment Scripts
- `deploy.sh` - Main deployment script that sets up everything
- `setup_database.sh` - Sets up PostgreSQL database with sample data
- `setup_vllm.sh` - Starts vLLM server with Granite model
- `setup_streamlit.sh` - Starts Streamlit web application
- `stop_services.sh` - Cleanly stops all services

### Configuration
- `requirements.txt` - Python dependencies
- `README.md` - This file

## Quick Start

### Prerequisites
- RHEL 9.x server with GPU support
- Podman installed and configured for GPU access
- Python 3.8+ with pip
- tmux (for session management)
- Hugging Face account and token

### One-Command Deployment

1. Set your Hugging Face token:
   ```bash
   export HUGGING_FACE_HUB_TOKEN="your_token_here"
   ```

2. Run the deployment script:
   ```bash
   chmod +x app/deploy.sh
   ./app/deploy.sh
   ```

3. Access the demo at: `http://your-server-ip:8501`

### Manual Setup (Alternative)

If you prefer to set up components individually:

```bash
# 1. Start database
chmod +x app/setup_database.sh
./app/setup_database.sh

# 2. Start vLLM server
export HUGGING_FACE_HUB_TOKEN="your_token_here"
chmod +x app/setup_vllm.sh
./app/setup_vllm.sh

# 3. Start Streamlit app
chmod +x app/setup_streamlit.sh
./app/setup_streamlit.sh
```

## Usage

### Web Interface
- Navigate to `http://your-server-ip:8501`
- Use the sample prompts or type your own questions
- The agent will automatically use tools when needed

### Sample Prompts
- "Review the current opportunities for ACME Corp"
- "Get a list of support cases for account 1 and analyze their severity"
- "Analyze the health status of account 1 based on support cases"

### Command Line Interface
```bash
python3 app/simple_agentic_demo.py
```

## Available Tools

The agent has access to these CRM tools:

1. **get_opportunities** - Retrieve active sales opportunities
2. **get_support_cases** - Get support cases for an account
3. **get_account_info** - Get comprehensive account information
4. **analyze_account_health** - Analyze account health based on support activity

## Monitoring and Debugging

### View Service Status
```bash
# Check running services
tmux list-sessions

# Monitor specific service
tmux attach-session -t vllm-demo      # vLLM logs
tmux attach-session -t streamlit-demo # Streamlit logs
```

### Debug Information
The Streamlit UI includes a debug panel showing:
- Agent configuration
- Available tools
- Environment variables
- Connection status

### Log Files
Services run in tmux sessions, so logs are viewable by attaching to the respective sessions.

## Configuration

### Environment Variables
- `VLLM_ENDPOINT` - vLLM server endpoint (default: localhost:8000)
- `MODEL_NAME` - Model name (default: ibm-granite/granite-3.3-2b-instruct)
- `DB_HOST` - Database host (default: localhost)
- `DB_PORT` - Database port (default: 5432)
- `DB_NAME` - Database name (default: claimdb)
- `DB_USER` - Database user (default: claimdb)
- `DB_PASSWORD` - Database password (default: claimdb)
- `HUGGING_FACE_HUB_TOKEN` - Required for model downloads

### Customization
- Modify `db_tools.py` to add new database tools
- Update `agent.py` to change tool calling behavior
- Edit `streamlit_app.py` to customize the UI

## Stopping Services

```bash
chmod +x app/stop_services.sh
./app/stop_services.sh
```

This will cleanly stop all containers and tmux sessions.

## Troubleshooting

### Common Issues

1. **GPU Not Detected**
   ```bash
   # Test GPU access
   podman run --rm --device nvidia.com/gpu=all \
     docker.io/nvidia/cuda:11.0.3-base-ubuntu20.04 nvidia-smi
   ```

2. **Database Connection Failed**
   ```bash
   # Check if PostgreSQL is running
   podman ps | grep postgres-demo
   # Check port
   nc -z localhost 5432
   ```

3. **vLLM Model Loading Issues**
   ```bash
   # Check vLLM logs
   tmux attach-session -t vllm-demo
   # Verify Hugging Face token
   echo $HUGGING_FACE_HUB_TOKEN
   ```

4. **Streamlit Not Starting**
   ```bash
   # Check Python dependencies
   python3 -c "import streamlit, psycopg2, requests"
   # Install if missing
   pip3 install --user -r app/requirements.txt
   ```

### Getting Help
- Check tmux sessions: `tmux list-sessions`
- View container status: `podman ps -a`
- Check port usage: `netstat -tlnp`

## Differences from Original Demo

| Feature | Original Demo | Simplified Demo |
|---------|---------------|-----------------|
| Framework | Llama Stack + MCP | Direct vLLM calls |
| Tool Calling | MCP protocol | Pattern matching |
| Setup Complexity | High (multiple dependencies) | Low (3 containers) |
| Deployment | Multi-step manual | Single script |
| Dependencies | Many (Node.js, MCP servers, etc.) | Few (Python + containers) |
| Debugging | Complex distributed logs | Simple tmux sessions |

## Performance Considerations

- **Model Loading**: First startup takes 5-10 minutes to download the Granite model
- **Memory Usage**: Requires ~8GB GPU memory for the 2B model
- **Response Time**: Typically 2-5 seconds for simple queries, 10-30 seconds with tools
- **Concurrent Users**: Single-user demo; not optimized for multiple concurrent sessions

## Security Notes

- The demo uses default passwords - change them for production use
- Hugging Face token is passed as environment variable - secure appropriately
- Database and vLLM endpoints are not encrypted - use behind firewall
- Streamlit runs on all interfaces (0.0.0.0) - restrict access as needed
