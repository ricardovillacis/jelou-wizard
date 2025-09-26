from abc import ABC, abstractmethod
import json
from typing import Type, TypeVar, Optional
from pydantic import BaseModel, ValidationError
from .anthropic import AnthropicChat
import instructor

T = TypeVar('T', bound=BaseModel)


class StructuredAnthropicChat(AnthropicChat,ABC):
    """
    A chat class that extends AnthropicChat to provide structured responses using Pydantic models.
    """
    
    def __init__(self):
        super().__init__()
        self.client = instructor.from_anthropic(client=self.client)
        self.response_format=None

    def send_message(self, content: str, max_tokens: int = 1000) -> str:
        # Add user message
        self.add_user_message(content)

        # Prepare the request parameters
        request_params = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": self.messages,
            "response_model":self.response_format
        }

        response = self.client.chat.completions.create_with_completion(model=self.model,max_tokens=max_tokens, messages=self.messages,response_model=self.response_format)
        model_response = response[0]                
        # Add assistant response to history
        self.add_assistant_message(self.get_model_assistant_message(model_response))
        
        return model_response    
    
    @abstractmethod
    def get_model_assistant_message(self, model_response: BaseModel) -> str:
        pass
