from typing import Dict
from pydantic import BaseModel, Field

# 1. Define your structured schema with Pydantic (or JSON schema)
class QuestionResponseStructure(BaseModel):
    user_description :str = Field(...,description="The questions and all what the user said about the questions well redacted and formatted without mentioning the user.")
    bot_response:str = Field(..., description="Bot response.")
    all_questions_answered:bool = Field(..., description="All questions have been answered")
    finished :bool = Field(...,description="After all questions have been anweserd and  the user says that the info is correct.")
    updated_slots: Dict[str, str] = Field(...,description="Questions as key(Write is as a section) and answers as values of what the user has answered.")