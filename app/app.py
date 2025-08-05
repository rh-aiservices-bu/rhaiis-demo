from flask import Flask, request, jsonify
import os
from granite_agent import GraniteAgent

app = Flask(__name__)

# Initialize the Granite agent
print("Initializing Granite agent...")
agent = GraniteAgent()
print("Granite agent initialized successfully!")

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
            return {'error': 'Missing message in request'}, 400
        
        message = data['message']
        response = agent.chat(message)
        
        return {
            'response': response,
            'status': 'success'
        }, 200
        
    except Exception as e:
        return {
            'error': f'Error processing request: {str(e)}',
            'status': 'error'
        }, 500

@app.route('/db/sales', methods=['GET'])
def get_sales():
    """Get sales opportunities"""
    try:
        opportunities = agent.db_tools.get_opportunities()
        return {
            'data': opportunities,
            'count': len(opportunities),
            'status': 'success'
        }, 200
    except Exception as e:
        return {
            'error': f'Error fetching sales data: {str(e)}',
            'status': 'error'
        }, 500

@app.route('/db/accounts', methods=['GET'])
def get_accounts():
    """Get customer accounts"""
    try:
        accounts = agent.db_tools.get_accounts()
        return {
            'data': accounts,
            'count': len(accounts),
            'status': 'success'
        }, 200
    except Exception as e:
        return {
            'error': f'Error fetching accounts data: {str(e)}',
            'status': 'error'
        }, 500

@app.route('/db/support', methods=['GET'])
def get_support():
    """Get support cases"""
    try:
        cases = agent.db_tools.get_support_cases()
        return {
            'data': cases,
            'count': len(cases),
            'status': 'success'
        }, 200
    except Exception as e:
        return {
            'error': f'Error fetching support data: {str(e)}',
            'status': 'error'
        }, 500

@app.route('/db/health', methods=['GET'])
def analyze_account_health():
    """Get account health metrics"""
    try:
        health_data = agent.db_tools.analyze_account_health()
        return {
            'data': health_data,
            'count': len(health_data),
            'status': 'success'
        }, 200
    except Exception as e:
        return {
            'error': f'Error fetching health data: {str(e)}',
            'status': 'error'
        }, 500

if __name__ == '__main__':
    print("Starting Flask CRM AI Agent Service...")
    app.run(host='0.0.0.0', port=5000, debug=False)
