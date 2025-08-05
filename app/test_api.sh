#!/bin/bash

API_BASE="http://localhost:5000"

echo "=========================================="
echo "   Testing Red Hat AI Inference Server"
echo "   Flask API with Granite Agent"
echo "=========================================="

echo ""
echo "1. Health Check"
echo "----------------------------------------"
curl -X GET "$API_BASE/health"
echo ""

echo ""
echo "2. vLLM Service Status"
echo "----------------------------------------"
curl -X GET "$API_BASE/vllm/status"
echo ""

echo ""
echo "3. Get All Accounts"
echo "----------------------------------------"
curl -X GET "$API_BASE/agent/accounts"
echo ""

echo ""
echo "4. Get Specific Account"
echo "----------------------------------------"
curl -X GET "$API_BASE/agent/accounts?account_id=ACC001"
echo ""

echo ""
echo "5. Get All Opportunities"
echo "----------------------------------------"
curl -X GET "$API_BASE/agent/opportunities"
echo ""

echo ""
echo "6. Get Opportunities by Status"
echo "----------------------------------------"
curl -X GET "$API_BASE/agent/opportunities?status=Open"
echo ""

echo ""
echo "7. Get Support Cases by Priority"
echo "----------------------------------------"
curl -X GET "$API_BASE/agent/support-cases?priority=High"
echo ""

echo ""
echo "8. Analyze Account Health"
echo "----------------------------------------"
curl -X GET "$API_BASE/agent/account-health/ACC001"
echo ""

echo ""
echo "9. Chat with AI Agent - Simple Question"
echo "----------------------------------------"
curl -X POST "$API_BASE/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, can you tell me about our accounts?"
  }'
echo ""

echo ""
echo "10. Chat with AI Agent - Business Intelligence Query"
echo "----------------------------------------"
curl -X POST "$API_BASE/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the current open opportunities for TechCorp Industries?"
  }'
echo ""

echo ""
echo "11. Chat with AI Agent - Account Health Analysis"
echo "----------------------------------------"
curl -X POST "$API_BASE/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can you analyze the health of account ACC004 and tell me if there are any concerns?"
  }'
echo ""

echo ""
echo "12. Chat with AI Agent - Support Case Analysis"
echo "----------------------------------------"
curl -X POST "$API_BASE/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me all critical support cases and their current status"
  }'
echo ""

echo ""
echo "=========================================="
echo "   Testing Complete!"
echo "=========================================="
