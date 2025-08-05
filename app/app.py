from flask import Flask, request, jsonify
import os
from granite_agent import GraniteAgent

app = Flask(__name__)

# Initialize the Granite agent
agent = GraniteAgent(
    vllm_url=os.getenv('VLLM_URL', 'http://localhost:8000'),
    model_name=os.getenv('MODEL_NAME', 'ibm-granite/granite-3.3-2b-instruct')
)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {'status': 'AI Agent Service is running'}, 200

@app.route('/agent/chat', methods=['POST'])
def agent_chat():
    """Main chat endpoint for the AI agent"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return {'error': 'Message is required'}, 400
        
        message = data['message']
        conversation_history = data.get('conversation_history', [])
        
        result = agent.chat(message, conversation_history)
        
        return {
            'success': True,
            'response': result['response'],
            'tool_used': result.get('tool_used'),
            'tool_params': result.get('tool_params'),
            'tool_result': result.get('tool_result')
        }, 200
        
    except Exception as e:
        return {'error': f'Internal server error: {str(e)}'}, 500

@app.route('/agent/opportunities', methods=['GET'])
def get_opportunities():
    """Direct endpoint to get opportunities"""
    try:
        account_id = request.args.get('account_id')
        status = request.args.get('status')
        
        result = agent.db_tools.get_opportunities(account_id=account_id, status=status)
        
        return {
            'success': True,
            'data': result
        }, 200
        
    except Exception as e:
        return {'error': f'Error fetching opportunities: {str(e)}'}, 500

@app.route('/agent/support-cases', methods=['GET'])
def get_support_cases():
    """Direct endpoint to get support cases"""
    try:
        account_id = request.args.get('account_id')
        priority = request.args.get('priority')
        
        result = agent.db_tools.get_support_cases(account_id=account_id, priority=priority)
        
        return {
            'success': True,
            'data': result
        }, 200
        
    except Exception as e:
        return {'error': f'Error fetching support cases: {str(e)}'}, 500

@app.route('/agent/accounts', methods=['GET'])
def get_accounts():
    """Direct endpoint to get accounts"""
    try:
        account_id = request.args.get('account_id')
        
        result = agent.db_tools.get_accounts(account_id=account_id)
        
        return {
            'success': True,
            'data': result
        }, 200
        
    except Exception as e:
        return {'error': f'Error fetching accounts: {str(e)}'}, 500

@app.route('/agent/account-health/<account_id>', methods=['GET'])
def analyze_account_health(account_id):
    """Direct endpoint to analyze account health"""
    try:
        result = agent.db_tools.analyze_account_health(account_id=account_id)
        
        return {
            'success': True,
            'data': result
        }, 200
        
    except Exception as e:
        return {'error': f'Error analyzing account health: {str(e)}'}, 500

@app.route('/vllm/status', methods=['GET'])
def vllm_status():
    """Check vLLM service status"""
    try:
        import requests
        response = requests.get(f"{agent.vllm_url}/health", timeout=5)
        if response.status_code == 200:
            return {'status': 'vLLM service is running'}, 200
        else:
            return {'status': 'vLLM service is not responding properly'}, 503
    except Exception as e:
        return {'status': f'vLLM service is not available: {str(e)}'}, 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
