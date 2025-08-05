# Red Hat AI Inference Server Demo - Testing Checklist

This checklist ensures all components of the RHEL vLLM demo are properly configured and functioning.

## Pre-Deployment Verification

### System Requirements
- [ ] RHEL 9.x server available
- [ ] NVIDIA GPU with 24GB+ VRAM detected
- [ ] SSH access configured
- [ ] Sudo privileges confirmed
- [ ] Internet connectivity verified

### Prerequisites Setup
- [ ] Hugging Face account created
- [ ] Hugging Face token generated and secured
- [ ] SSH keys configured for server access

## Installation Testing

### NVIDIA Driver Installation
- [ ] Kernel development tools installed successfully
- [ ] EPEL repository added
- [ ] NVIDIA CUDA repository configured
- [ ] NVIDIA drivers installed without errors
- [ ] System rebooted successfully
- [ ] `nvidia-smi` command shows GPU information
- [ ] GPU memory and driver version displayed correctly

### Container Runtime Setup
- [ ] NVIDIA Container Toolkit repository added
- [ ] Experimental features enabled
- [ ] nvidia-container-toolkit and podman installed
- [ ] CDI specification generated at `/etc/cdi/nvidia.yaml`
- [ ] GPU test container runs successfully:
  ```bash
  sudo podman run --rm --device nvidia.com/gpu=all \
    docker.io/nvidia/cuda:11.0.3-base-ubuntu20.04 nvidia-smi
  ```

## vLLM Deployment Testing

### Environment Setup
- [ ] Hugging Face token exported correctly
- [ ] Model cache directory created
- [ ] tmux session management working

### vLLM Server Deployment
- [ ] Red Hat AI Inference Server container pulls successfully
- [ ] Model downloads without errors
- [ ] vLLM server starts and listens on port 8000
- [ ] Server shows "Application startup complete" message
- [ ] No GPU memory errors in logs

### API Testing
- [ ] Models endpoint responds correctly:
  ```bash
  curl http://localhost:8000/v1/models | jq .
  ```
- [ ] Chat completion API works:
  ```bash
  curl -H 'Content-Type: application/json' \
    http://localhost:8000/v1/chat/completions \
    -d '{
      "model": "RedHatAI/Llama-3.2-1B-Instruct-FP8",
      "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
      ]
    }' | jq -r .choices[0].message.content
  ```
- [ ] Response is coherent and properly formatted

## Demo Application Testing

### Database Setup
- [ ] PostgreSQL container starts successfully
- [ ] Database is accessible on port 5432
- [ ] Import script runs without errors
- [ ] Sample data is loaded correctly

### MCP Servers Setup
- [ ] Node.js and npm installed
- [ ] CRM MCP server dependencies installed
- [ ] MCP server starts without errors
- [ ] Database connection established

### Llama Stack Deployment
- [ ] Llama Stack configuration file is correct
- [ ] Environment variables set properly
- [ ] Llama Stack container starts successfully
- [ ] Connects to vLLM server correctly
- [ ] API endpoints are accessible

### Tool Group Registration
- [ ] CRM MCP server registered successfully:
  ```bash
  curl -X POST -H "Content-Type: application/json" \
    --data '{
      "provider_id": "model-context-protocol",
      "toolgroup_id": "mcp::crm",
      "mcp_endpoint": {"uri": "http://host.containers.internal:8000/sse"}
    }' \
    http://localhost:5001/v1/toolgroups
  ```
- [ ] Registration returns success response
- [ ] Tool group appears in available tools list

## UI Testing

### UI Deployment
- [ ] UI container builds successfully
- [ ] UI starts on port 8501
- [ ] Streamlit interface loads without errors
- [ ] Connection to Llama Stack established

### Functional Testing
- [ ] UI displays conversation interface
- [ ] Can send messages through the interface
- [ ] Messages are processed by the backend
- [ ] Responses are displayed correctly
- [ ] Tool usage is visible in the interface

## End-to-End Workflow Testing

### Sample Workflow Execution
Test the complete agentic workflow with these steps:

- [ ] **Step 1**: "Review the current opportunities for ACME"
  - [ ] Request processed successfully
  - [ ] CRM data retrieved
  - [ ] Response shows opportunity information

- [ ] **Step 2**: "Get a list of support cases for the account"
  - [ ] Support cases retrieved from database
  - [ ] Data properly formatted and displayed

- [ ] **Step 3**: "Determine the status of the account based on the cases"
  - [ ] AI analyzes support case data
  - [ ] Provides reasonable assessment (happy/unhappy/neutral)
  - [ ] Reasoning is explained

- [ ] **Step 4**: "Generate a PDF document with a summary"
  - [ ] PDF generation tool is invoked
  - [ ] PDF is created successfully
  - [ ] Content includes summary of cases and status

- [ ] **Step 5**: "Send a slack message with the status"
  - [ ] Slack integration works (if configured)
  - [ ] Message is sent to appropriate channel
  - [ ] Content is relevant and well-formatted

## Performance Testing

### Resource Utilization
- [ ] GPU memory usage is reasonable (not exceeding 90%)
- [ ] CPU usage is within acceptable limits
- [ ] Memory usage is stable over time
- [ ] No memory leaks detected

### Response Times
- [ ] Simple queries respond within 5 seconds
- [ ] Complex queries with tool usage complete within 30 seconds
- [ ] UI remains responsive during processing
- [ ] Multiple concurrent requests handled properly

## Error Handling Testing

### Network Issues
- [ ] Graceful handling of network interruptions
- [ ] Proper error messages displayed
- [ ] System recovers after network restoration

### Resource Limitations
- [ ] Handles GPU memory limitations gracefully
- [ ] Provides clear error messages for resource issues
- [ ] Degrades gracefully under high load

### Configuration Errors
- [ ] Clear error messages for misconfiguration
- [ ] Helpful troubleshooting guidance provided
- [ ] System doesn't crash on configuration errors

## Security Testing

### Access Control
- [ ] Hugging Face token is properly secured
- [ ] No sensitive information exposed in logs
- [ ] Container security options are appropriate
- [ ] Network access is properly restricted

### Data Privacy
- [ ] No sensitive data logged unnecessarily
- [ ] Temporary files are cleaned up properly
- [ ] Model cache permissions are appropriate

## Documentation Validation

### Setup Documentation
- [ ] All commands in documentation work as written
- [ ] Prerequisites are clearly stated
- [ ] Installation steps are in correct order
- [ ] Error conditions are documented

### Troubleshooting Guide
- [ ] Common issues are covered
- [ ] Solutions are tested and verified
- [ ] Log analysis guidance is helpful
- [ ] Performance tuning tips are effective

## Production Readiness

### Monitoring
- [ ] Log aggregation strategy defined
- [ ] Performance monitoring metrics identified
- [ ] Health check endpoints functional
- [ ] Alerting thresholds established

### Backup and Recovery
- [ ] Model cache backup strategy defined
- [ ] Configuration backup procedures documented
- [ ] Recovery procedures tested
- [ ] Data persistence strategy validated

### Scalability
- [ ] Multi-GPU configuration tested (if applicable)
- [ ] Load balancing options identified
- [ ] Horizontal scaling paths documented
- [ ] Resource requirements for scale documented

## Sign-off

### Component Testing
- [ ] NVIDIA drivers: ✅ Tested by: _______ Date: _______
- [ ] Container runtime: ✅ Tested by: _______ Date: _______
- [ ] vLLM server: ✅ Tested by: _______ Date: _______
- [ ] Demo application: ✅ Tested by: _______ Date: _______
- [ ] UI interface: ✅ Tested by: _______ Date: _______

### Integration Testing
- [ ] End-to-end workflow: ✅ Tested by: _______ Date: _______
- [ ] Performance testing: ✅ Tested by: _______ Date: _______
- [ ] Error handling: ✅ Tested by: _______ Date: _______

### Documentation Review
- [ ] Setup guide: ✅ Reviewed by: _______ Date: _______
- [ ] Testing checklist: ✅ Reviewed by: _______ Date: _______
- [ ] Troubleshooting guide: ✅ Reviewed by: _______ Date: _______

### Final Approval
- [ ] Demo ready for presentation: ✅ Approved by: _______ Date: _______
- [ ] Documentation complete: ✅ Approved by: _______ Date: _______
- [ ] Production deployment ready: ✅ Approved by: _______ Date: _______

## Notes

Record any issues encountered during testing:

```
Date: _______
Issue: ________________________________
Resolution: ____________________________
Tester: _______________________________

Date: _______
Issue: ________________________________
Resolution: ____________________________
Tester: _______________________________
```

## Next Steps After Testing

1. **Address any failed test items**
2. **Update documentation based on testing findings**
3. **Create deployment automation scripts**
4. **Develop monitoring and alerting setup**
5. **Plan production deployment strategy**
