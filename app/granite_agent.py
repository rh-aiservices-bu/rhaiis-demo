import json
import requests
import re
from typing import Dict, Any, List, Optional
from db_tools import DatabaseTools

class GraniteAgent:
    def __init__(self, vllm_url: str = "http://localhost:8000", model_name: str = "ibm-granite/granite-3.3-2b-instruct"):
        self.vllm_url = vllm_url
        self.model_name = model_name
        self.db_tools = DatabaseTools()
        self.system_prompt = """You are a helpful business intelligence assistant with access to a CRM database. 
You can help analyze customer data, opportunities, support cases, and account health.

Available tools:
- get_opportunities(account_id=None, status=None): Get sales opportunities
- get_support_cases(account_id=None, priority=None): Get support cases  
- get_accounts(account_id=None): Get account information
- analyze_account_health(account_id): Analyze overall account health

When you need to use a tool, format your response as:
TOOL_CALL: function_name(param1="value1", param2="value2")

Always provide helpful analysis and insights based on the data you retrieve."""
    
    def _call_vllm(self, messages: List[Dict[str, str]], max_tokens: int = 512) -> str:
        """Call the vLLM API"""
        try:
            payload = {
                "model": self.model_name,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.1
            }
            
            response = requests.post(
                f"{self.vllm_url}/v1/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return f"Error calling vLLM: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Error calling vLLM: {str(e)}"
    
    def _parse_tool_call(self, text: str) -> Optional[tuple]:
        """Parse tool call from model response"""
        pattern = r'TOOL_CALL:\s*(\w+)\((.*?)\)'
        match = re.search(pattern, text)
        
        if match:
            function_name = match.group(1)
            params_str = match.group(2)
            
            # Parse parameters
            params = {}
            if params_str.strip():
                # Simple parameter parsing
                param_pairs = params_str.split(',')
                for pair in param_pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        if value.lower() == 'none':
                            value = None
                        params[key] = value
            
            return function_name, params
        return None
    
    def _execute_tool(self, function_name: str, params: Dict[str, Any]) -> str:
        """Execute a tool call"""
        try:
            if function_name == "get_opportunities":
                return self.db_tools.get_opportunities(**params)
            elif function_name == "get_support_cases":
                return self.db_tools.get_support_cases(**params)
            elif function_name == "get_accounts":
                return self.db_tools.get_accounts(**params)
            elif function_name == "analyze_account_health":
                return self.db_tools.analyze_account_health(**params)
            else:
                return f"Unknown function: {function_name}"
        except Exception as e:
            return f"Error executing {function_name}: {str(e)}"
    
    def chat(self, user_message: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Main chat interface with tool calling support"""
        if conversation_history is None:
            conversation_history = []
        
        # Build messages
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})
        
        # Get initial response
        response = self._call_vllm(messages)
        
        # Check for tool calls
        tool_call = self._parse_tool_call(response)
        if tool_call:
            function_name, params = tool_call
            tool_result = self._execute_tool(function_name, params)
            
            # Add tool result and get final response
            messages.append({"role": "assistant", "content": response})
            messages.append({"role": "user", "content": f"Tool result: {tool_result}"})
            
            final_response = self._call_vllm(messages)
            
            return {
                "response": final_response,
                "tool_used": function_name,
                "tool_params": params,
                "tool_result": tool_result
            }
        else:
            return {
                "response": response,
                "tool_used": None
            }
