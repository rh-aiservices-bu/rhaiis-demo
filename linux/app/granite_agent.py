import re
import json
import requests
from typing import List, Dict, Any, Optional
from db_tools import DatabaseTools

class GraniteAgent:
    """
    A Granite AI agent that can call database tools to answer CRM-related questions.
    This version uses Hugging Face Transformers pipeline directly instead of vLLM.
    """
    
    def __init__(self):
        self.db_tools = DatabaseTools()
        self.model = None
        self.tokenizer = None
        self._initialize_model()
        
    def _initialize_model(self):
        """Initialize the Granite model using Hugging Face Transformers"""
        try:
            from transformers import pipeline, AutoTokenizer
            import torch
            
            model_name = "ibm-granite/granite-3.3-2b-instruct"
            
            # Check if CUDA is available
            device = 0 if torch.cuda.is_available() else -1
            
            print(f"Loading model {model_name} on {'GPU' if device == 0 else 'CPU'}...")
            
            # Initialize the pipeline
            self.model = pipeline(
                "text-generation",
                model=model_name,
                tokenizer=model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device=device,
                trust_remote_code=True,
                return_full_text=False,
                max_new_tokens=1000,
                do_sample=True,
                temperature=0.7,
                pad_token_id=50256
            )
            
            print("Model loaded successfully!")
            
        except Exception as e:
            print(f"Error initializing model: {e}")
            self.model = None
    
    def chat(self, message: str) -> str:
        """
        Process a chat message and return a response, using tools when needed.
        """
        if not self.model:
            return "I'm sorry, the AI model is not available right now. Please try again later."
        
        try:
            # Check if the query needs database information
            if self._needs_database_info(message):
                return self._handle_database_query(message)
            else:
                return self._generate_simple_response(message)
                
        except Exception as e:
            print(f"Error in chat: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    def _needs_database_info(self, message: str) -> bool:
        """Check if the message requires database information"""
        db_keywords = [
            'sales', 'opportunity', 'opportunities', 'revenue', 'deal', 'deals',
            'account', 'accounts', 'customer', 'customers', 'client', 'clients',
            'support', 'case', 'cases', 'ticket', 'tickets', 'issue', 'issues',
            'pipeline', 'forecast', 'quota', 'target', 'performance', 'metrics',
            'health', 'score', 'satisfaction', 'churn', 'retention'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in db_keywords)
    
    def _handle_database_query(self, message: str) -> str:
        """Handle queries that need database information"""
        
        # Create a system prompt for the AI
        system_prompt = """You are a CRM Business Intelligence Assistant. You have access to the following database tools:

1. get_opportunities() - Get all sales opportunities
2. get_support_cases() - Get all support cases  
3. get_accounts() - Get all customer accounts
4. analyze_account_health() - Get account health metrics

When a user asks about CRM data, determine which tool(s) to call and then provide insights based on the data.

Available tools:
- get_opportunities
- get_support_cases  
- get_accounts
- analyze_account_health

User question: {message}

Based on this question, which database tool should I call? Respond with just the tool name."""

        # Determine which tool to call
        tool_prompt = system_prompt.format(message=message)
        
        try:
            tool_response = self.model(tool_prompt, max_new_tokens=50)
            tool_name = tool_response[0]['generated_text'].strip().lower()
            
            # Call the appropriate database tool
            data = None
            if 'sales' in tool_name or 'opportunity' in tool_name:
                data = self.db_tools.get_opportunities()
                data_type = "sales opportunities"
            elif 'support' in tool_name or 'case' in tool_name:
                data = self.db_tools.get_support_cases()
                data_type = "support cases"
            elif 'account_health' in tool_name or 'health' in tool_name:
                data = self.db_tools.analyze_account_health("ACC001")  # Sample account
                data_type = "account health metrics"
            elif 'account' in tool_name:
                data = self.db_tools.get_accounts()
                data_type = "customer accounts"
            else:
                # Default to sales opportunities
                data = self.db_tools.get_opportunities()
                data_type = "sales opportunities"
            
            # Generate response based on the data
            return self._generate_data_response(message, data, data_type)
            
        except Exception as e:
            print(f"Error in database query handling: {e}")
            return "I'm having trouble accessing the database right now. Please try again later."
    
    def _generate_data_response(self, message: str, data: Any, data_type: str) -> str:
        """Generate a response based on database data"""
        
        # Handle different data types
        if isinstance(data, str):
            # If data is a string (like from db_tools methods), parse it
            try:
                import ast
                data = ast.literal_eval(data)
            except:
                # If parsing fails, use the string directly for analysis
                analysis_prompt = f"""You are a CRM Business Intelligence Assistant. A user asked: "{message}"

I retrieved the following {data_type} information:

{data}

Please provide a helpful business analysis and insights based on this data. Be specific about numbers, trends, and actionable recommendations."""
                
                try:
                    response = self.model(analysis_prompt, max_new_tokens=300)
                    return response[0]['generated_text'].strip()
                except Exception as e:
                    print(f"Error generating string data response: {e}")
                    return f"I found {data_type} data but had trouble analyzing it. Here's the raw information: {str(data)[:200]}..."
        
        if not data or (isinstance(data, list) and len(data) == 0):
            return f"I found no {data_type} in the database."
        
        # Create a clean, readable summary of the data
        if isinstance(data, list):
            data_summary = self._format_data_summary(data[:3])  # Show first 3 records
            record_count = len(data)
        else:
            data_summary = str(data)[:300]  # Truncate long strings
            record_count = 1
        
        analysis_prompt = f"""You are a CRM Business Intelligence Assistant. A user asked: "{message}"

I retrieved the following {data_type} data:

{data_summary}

Total records: {record_count}

Please provide a helpful business analysis and insights based on this data. Be specific about numbers, trends, and actionable recommendations. Do not include the raw data in your response."""

        try:
            response = self.model(analysis_prompt, max_new_tokens=300)
            return response[0]['generated_text'].strip()
        except Exception as e:
            print(f"Error generating data response: {e}")
            return f"I found {record_count} {data_type}. Here's a summary: {data_summary}"
    
    def _format_data_summary(self, data: List[Dict]) -> str:
        """Format data into a readable summary for the AI model"""
        if not data:
            return "No data available"
        
        summary_lines = []
        for i, record in enumerate(data, 1):
            if isinstance(record, dict):
                # Create a readable summary of key fields
                key_info = []
                for key, value in record.items():
                    if key in ['opportunity_name', 'company_name', 'subject', 'account_id', 'amount', 'stage', 'priority', 'status']:
                        key_info.append(f"{key}: {value}")
                
                if key_info:
                    summary_lines.append(f"Record {i}: {', '.join(key_info[:4])}")  # Show first 4 fields
                else:
                    summary_lines.append(f"Record {i}: {str(record)[:100]}...")
            else:
                summary_lines.append(f"Record {i}: {str(record)[:100]}...")
        
        return "\n".join(summary_lines)
    
    def _generate_simple_response(self, message: str) -> str:
        """Generate a simple response for non-database queries"""
        
        prompt = f"""You are a helpful CRM Business Intelligence Assistant. Please provide a brief, helpful response to: {message}"""
        
        try:
            response = self.model(prompt, max_new_tokens=150)
            return response[0]['generated_text'].strip()
        except Exception as e:
            print(f"Error generating simple response: {e}")
            return "I'm here to help with CRM and business intelligence questions. How can I assist you today?"

# Test the agent if run directly
if __name__ == "__main__":
    agent = GraniteAgent()
    
    # Test query
    response = agent.chat("What are our current sales opportunities?")
    print("Response:", response)
