import os
from typing import List, Dict, Any, Optional
from anthropic import Anthropic
from pydantic import BaseModel


class AnthropicChat:
    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        # Load environment variables from .env if present
        if os.path.exists('.env'):
            from dotenv import load_dotenv
            load_dotenv()
        
        # Initialize Anthropic client
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.messages: List[Dict[str, Any]] = []
    
    def add_system_message(self, content: str) -> None:
        """Add a system message to the conversation."""
        self.messages.append({"role": "user", "content": content})
    
    def add_user_message(self, content: str) -> None:
        """Add a user message to the conversation."""
        self.messages.append({"role": "user", "content": content})
    
    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to the conversation."""
        self.messages.append({"role": "assistant", "content": content})
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """Get the current message history."""
        return self.messages.copy()
    
    def send_message(self, content: str, max_tokens: int = 1000, response_format: Optional[BaseModel] = None) -> str:
        """Send a message and get the assistant's response."""
        # Add user message
        self.add_user_message(content)

        # Prepare the request parameters
        request_params = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": self.messages
        }
        
        # Add response format if provided
        if response_format:
            request_params["response_format"] = {"type": "json_object"}

        response = self.client.messages.create(**request_params)
        
        # Extract and add assistant response
        assistant_content = ""
        if response.content:
            for block in response.content:
                if hasattr(block, 'text'):
                    assistant_content += block.text
                elif isinstance(block, dict) and 'text' in block:
                    assistant_content += block['text']
        
        # Add assistant response to history
        self.add_assistant_message(assistant_content)
        
        return assistant_content
