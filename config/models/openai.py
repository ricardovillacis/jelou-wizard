import os
from typing import List, Dict, Any, Optional
from openai import OpenAI
from pydantic import BaseModel


class OpenAIChat:
    def __init__(self, model: str = "gpt-5"):
        # Load environment variables from .env if present
        if os.path.exists('.env'):
            from dotenv import load_dotenv
            load_dotenv()

        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.messages: List[Dict[str, Any]] = []

    def add_system_message(self, content: str) -> None:
        self.messages.append({"role": "system", "content": content})

    def add_user_message(self, content: str) -> None:
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str) -> None:
        self.messages.append({"role": "assistant", "content": content})

    def get_messages(self) -> List[Dict[str, Any]]:
        return self.messages.copy()

    def send_message(self, content: str, max_tokens: int = 1000, response_format: Optional[BaseModel] = None) -> str:
        # Add user message
        self.add_user_message(content)

        request_params: Dict[str, Any] = {
            "model": self.model,
            "messages": self.messages,
            "max_tokens": max_tokens,
        }

        # OpenAI's response_format can be {"type": "json_object"}
        if response_format is not None:
            request_params["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(**request_params)

        assistant_content = response.choices[0].message.content if response.choices else ""
        self.add_assistant_message(assistant_content)
        return assistant_content



