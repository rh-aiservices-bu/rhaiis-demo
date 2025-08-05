#!/usr/bin/env python3
"""
Simple Agentic AI Demo

This script demonstrates a basic AI assistant functionality using the Granite model in vLLM.
"""

import requests
import json

class GraniteAgent:
    def __init__(self, endpoint, model):
        self.endpoint = endpoint
        self.model = model

    def send_message(self, messages):
        data = {
            "model": self.model,
            "messages": messages
        }
        response = requests.post(f"http://{self.endpoint}/v1/chat/completions", 
                                 headers={'Content-Type': 'application/json'},
                                 data=json.dumps(data))
        return response.json()

if __name__ == "__main__":
    endpoint = "localhost:8000"
    model = "ibm-granite/granite-3.3-2b-instruct"
    agent = GraniteAgent(endpoint, model)

    user_prompts = [
        "Hello, how can you assist me today?",
        "What opportunities are available with Red Hat?"
    ]

    for prompt in user_prompts:
        response = agent.send_message([
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ])
        print("User:", prompt)
        print("Assistant:", response['choices'][0]['message']['content'])

