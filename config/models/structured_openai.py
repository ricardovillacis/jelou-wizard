from abc import ABC, abstractmethod
from typing import TypeVar
from pydantic import BaseModel
from .openai import OpenAIChat
import instructor

T = TypeVar('T', bound=BaseModel)


class StructuredOpenAIChat(OpenAIChat, ABC):
    """
    A chat class that extends OpenAIChat to provide structured responses using Pydantic models.
    """

    def __init__(self):
        super().__init__()
        # Wrap OpenAI client for structured outputs
        self.client = instructor.from_openai(client=self.client)
        self.response_format = None

    def send_message(self, content: str, max_tokens: int = 1000):
        # Add user message
        self.add_user_message(content)

        # Use instructor to parse into the provided Pydantic model
        response = self.client.chat.completions.create_with_completion(
            model=self.model,
            messages=self.messages,
            response_model=self.response_format,
        )
        model_response = response[0]
        # Store assistant-friendly message
        self.add_assistant_message(self.get_model_assistant_message(model_response))
        return model_response

    @abstractmethod
    def get_model_assistant_message(self, model_response: BaseModel) -> str:
        pass




