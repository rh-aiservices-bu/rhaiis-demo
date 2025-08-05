#!/usr/bin/env python3
"""
Red Hat AI Agent Demo - Streamlit UI

A simplified Streamlit interface for the Red Hat AI Agent demo that works
directly with vLLM and Granite models without MCP or Llama Stack.
"""

import streamlit as st
import os
import json
from datetime import datetime

from agent import GraniteAgent, Tool
from db_tools import DatabaseConnection, create_crm_tools


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "agent" not in st.session_state:
        st.session_state.agent = None
    if "db_connection" not in st.session_state:
        st.session_state.db_connection = None
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "agent_initialized" not in st.session_state:
        st.session_state.agent_initialized = False


def setup_agent():
    """Set up the agent with database connection and tools"""
    try:
        # Database configuration from environment or defaults
        db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_NAME', 'claimdb'),
            'user': os.getenv('DB_USER', 'claimdb'),
            'password': os.getenv('DB_PASSWORD', 'claimdb')
        }
        
        # Initialize database connection
        if not st.session_state.db_connection:
            st.session_state.db_connection = DatabaseConnection(**db_config)
            if not st.session_state.db_connection.connect():
                st.error("Failed to connect to database. Please check your database configuration.")
                return False
        
        # vLLM configuration
        vllm_endpoint = os.getenv('VLLM_ENDPOINT', 'localhost:8000')
        model_name = os.getenv('MODEL_NAME', 'ibm-granite/granite-3.3-2b-instruct')
        
        # Initialize agent
        if not st.session_state.agent:
            st.session_state.agent = GraniteAgent(
                endpoint=vllm_endpoint,
                model=model_name,
                max_tokens=3000
            )
            
            # Add CRM tools
            crm_tools = create_crm_tools(st.session_state.db_connection)
            for tool in crm_tools:
                st.session_state.agent.add_tool(tool)
                
        st.session_state.agent_initialized = True
        return True
        
    except Exception as e:
        st.error(f"Error setting up agent: {str(e)}")
        return False


def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Red Hat AI Agent Demo",
        page_icon="🔴",
        layout="wide"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar with configuration
    with st.sidebar:
        st.image("https://i.postimg.cc/MHZB5tmL/Screenshot-2025-04-21-at-5-58-46-PM.png", width=200)
        st.title("ParasolCloud")
        st.caption("Secure Cloud Solutions for a Brighter Business")
        
        st.divider()
        
        # Configuration section
        st.subheader("Configuration")
        
        # vLLM settings
        with st.expander("vLLM Settings", expanded=False):
            vllm_endpoint = st.text_input(
                "vLLM Endpoint", 
                value=os.getenv('VLLM_ENDPOINT', 'localhost:8000'),
                help="The endpoint where vLLM server is running"
            )
            model_name = st.text_input(
                "Model Name",
                value=os.getenv('MODEL_NAME', 'ibm-granite/granite-3.3-2b-instruct'),
                help="The name of the model being served by vLLM"
            )
            
        # Database settings
        with st.expander("Database Settings", expanded=False):
            db_host = st.text_input("Database Host", value=os.getenv('DB_HOST', 'localhost'))
            db_port = st.number_input("Database Port", value=int(os.getenv('DB_PORT', '5432')))
            db_name = st.text_input("Database Name", value=os.getenv('DB_NAME', 'claimdb'))
            db_user = st.text_input("Database User", value=os.getenv('DB_USER', 'claimdb'))
            db_password = st.text_input("Database Password", value=os.getenv('DB_PASSWORD', 'claimdb'), type="password")
            
        # Connection status
        if st.button("Initialize/Reconnect Agent"):
            # Update environment variables
            os.environ['VLLM_ENDPOINT'] = vllm_endpoint
            os.environ['MODEL_NAME'] = model_name
            os.environ['DB_HOST'] = db_host
            os.environ['DB_PORT'] = str(db_port)
            os.environ['DB_NAME'] = db_name
            os.environ['DB_USER'] = db_user
            os.environ['DB_PASSWORD'] = db_password
            
            # Reset session state
            st.session_state.agent = None
            st.session_state.db_connection = None
            st.session_state.agent_initialized = False
            
            # Reinitialize
            if setup_agent():
                st.success("Agent initialized successfully!")
            else:
                st.error("Failed to initialize agent")
                
        # Status indicators
        st.subheader("Status")
        if st.session_state.agent_initialized:
            st.success("🟢 Agent Ready")
        else:
            st.warning("🟡 Agent Not Initialized")
            
        if st.session_state.db_connection and st.session_state.db_connection.connection:
            st.success("🟢 Database Connected")
        else:
            st.error("🔴 Database Disconnected")
            
        # Clear conversation
        if st.button("Clear Conversation"):
            st.session_state.conversation_history = []
            if st.session_state.agent:
                st.session_state.agent.clear_history()
            st.rerun()
    
    # Main content area
    st.title("🤖 Red Hat AI Agent Demo")
    st.caption("Powered by Granite AI and Red Hat AI Inference Server (vLLM)")
    
    # Initialize agent if not done
    if not st.session_state.agent_initialized:
        with st.spinner("Initializing agent..."):
            if not setup_agent():
                st.error("Please check your configuration and try again.")
                st.stop()
    
    # Sample prompts
    st.subheader("Sample Prompts")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Review Opportunities", use_container_width=True):
            prompt = "Review the current opportunities for ACME Corp"
            st.session_state.current_prompt = prompt
            
    with col2:
        if st.button("🎫 Check Support Cases", use_container_width=True):
            prompt = "Get a list of support cases for account 1 and analyze their severity"
            st.session_state.current_prompt = prompt
            
    with col3:
        if st.button("💊 Account Health Analysis", use_container_width=True):
            prompt = "Analyze the health status of account 1 based on support cases and provide recommendations"
            st.session_state.current_prompt = prompt
    
    # Chat interface
    st.subheader("Chat Interface")
    
    # Display conversation history
    for message in st.session_state.conversation_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if "current_prompt" in st.session_state:
        user_input = st.session_state.current_prompt
        del st.session_state.current_prompt
    else:
        user_input = st.chat_input("Enter your message here...")
    
    if user_input:
        # Add user message to history
        st.session_state.conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.agent.chat(user_input)
                    st.markdown(response)
                    
                    # Add assistant response to history
                    st.session_state.conversation_history.append({
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.conversation_history.append({
                        "role": "assistant",
                        "content": error_msg,
                        "timestamp": datetime.now().isoformat()
                    })
    
    # Debug information
    with st.expander("Debug Information", expanded=False):
        st.subheader("Agent Status")
        if st.session_state.agent:
            st.json({
                "endpoint": st.session_state.agent.endpoint,
                "model": st.session_state.agent.model,
                "max_tokens": st.session_state.agent.max_tokens,
                "tools_available": list(st.session_state.agent.tools.keys()),
                "conversation_length": len(st.session_state.agent.conversation_history)
            })
        else:
            st.write("Agent not initialized")
            
        st.subheader("Environment Variables")
        env_vars = {
            "VLLM_ENDPOINT": os.getenv('VLLM_ENDPOINT', 'Not set'),
            "MODEL_NAME": os.getenv('MODEL_NAME', 'Not set'),
            "DB_HOST": os.getenv('DB_HOST', 'Not set'),
            "DB_NAME": os.getenv('DB_NAME', 'Not set'),
            "DB_USER": os.getenv('DB_USER', 'Not set')
        }
        st.json(env_vars)


if __name__ == "__main__":
    main()
