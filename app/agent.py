#!/usr/bin/env python3
"""
Red Hat AI Agent Demo - Core Agent Class

This module provides the core agent functionality that works directly with vLLM
and Granite models, without requiring MCP or Llama Stack.
"""

import json
import re
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Tool:
    """Represents a tool that the agent can use"""
    name: str
    description: str
    parameters: Dict[str, Any]
    function: callable


class GraniteAgent:
    """
    A simplified AI agent that works directly with vLLM and Granite models.
    Includes tool calling capabilities for agentic behavior.
    """
    
    def __init__(self, endpoint: str, model: str, max_tokens: int = 3000):
        self.endpoint = endpoint
        self.model = model
        self.max_tokens = max_tokens
        self.tools = {}
        self.conversation_history = []
        
    def add_tool(self, tool: Tool):
        """Add a tool to the agent's toolkit"""
        self.tools[tool.name] = tool
        
    def get_tools_description(self) -> str:
        """Generate a description of available tools for the system prompt"""
        if not self.tools:
            return ""
            
        tools_desc = "\n\nYou have access to the following tools:\n"
        for tool_name, tool in self.tools.items():
            tools_desc += f"\n- {tool_name}: {tool.description}"
            if tool.parameters:
                tools_desc += f"\n  Parameters: {json.dumps(tool.parameters, indent=2)}"
        
        tools_desc += "\n\nTo use a tool, respond with: TOOL_CALL: {tool_name} {parameters_as_json}"
        tools_desc += "\nExample: TOOL_CALL: get_opportunities {\"account_id\": \"1\"}"
        
        return tools_desc
        
    def parse_tool_calls(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse tool calls from the agent's response"""
        tool_calls = []
        
        # Look for TOOL_CALL patterns
        pattern = r'TOOL_CALL:\s*(\w+)\s*({.*?})?'
        matches = re.findall(pattern, response_text, re.DOTALL)
        
        for match in matches:
            tool_name = match[0]
            params_str = match[1].strip() if match[1] else "{}"
            
            try:
                params = json.loads(params_str)
            except json.JSONDecodeError:
                params = {}
                
            tool_calls.append({
                "name": tool_name,
                "parameters": params
            })
            
        return tool_calls
        
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Execute a tool and return the result"""
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}"
            
        try:
            tool = self.tools[tool_name]
            result = tool.function(**parameters)
            return str(result)
        except Exception as e:
            return f"Error executing tool '{tool_name}': {str(e)}"
            
    def send_request(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Send a request to the vLLM server"""
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        try:
            response = requests.post(
                f"http://{self.endpoint}/v1/chat/completions",
                headers={'Content-Type': 'application/json'},
                data=json.dumps(data),
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
            
    def chat(self, user_message: str, system_prompt: Optional[str] = None) -> str:
        """
        Process a user message and return the agent's response.
        Handles tool calling automatically.
        """
        if system_prompt is None:
            system_prompt = (
                "You are a helpful AI assistant for ParasolCloud, a company providing "
                "secure cloud solutions. You help analyze customer accounts, opportunities, "
                "and support cases. Be professional, helpful, and detailed in your responses."
            )
            
        # Add tools description to system prompt
        full_system_prompt = system_prompt + self.get_tools_description()
        
        # Build messages
        messages = [{"role": "system", "content": full_system_prompt}]
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Send initial request
        response = self.send_request(messages)
        
        if "error" in response:
            return f"Error: {response['error']}"
            
        if "choices" not in response or not response["choices"]:
            return "Error: No response from model"
            
        assistant_response = response["choices"][0]["message"]["content"]
        
        # Check for tool calls
        tool_calls = self.parse_tool_calls(assistant_response)
        
        # Execute tools if found
        tool_results = []
        for tool_call in tool_calls:
            result = self.execute_tool(tool_call["name"], tool_call["parameters"])
            tool_results.append(f"Tool '{tool_call['name']}' result: {result}")
        
        # If tools were called, send results back to model for final response
        if tool_results:
            messages.append({"role": "assistant", "content": assistant_response})
            
            tool_context = "\n\n".join(tool_results)
            messages.append({
                "role": "user", 
                "content": f"Tool execution results:\n{tool_context}\n\nBased on these results, please provide a comprehensive response to the original question."
            })
            
            # Get final response
            final_response = self.send_request(messages)
            if "error" in final_response:
                return f"Error in final response: {final_response['error']}"
                
            if "choices" not in final_response or not final_response["choices"]:
                return "Error: No final response from model"
                
            final_text = final_response["choices"][0]["message"]["content"]
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": final_text})
            
            return final_text
        else:
            # No tools called, return direct response
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": assistant_response})
            
            return assistant_response
            
    def clear_history(self):
        """Clear the conversation history"""
        self.conversation_history = []
