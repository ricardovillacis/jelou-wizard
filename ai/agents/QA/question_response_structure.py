from pydantic import BaseModel, Field

# 1. Define your structured schema with Pydantic (or JSON schema)
class QuestionResponseStructure(BaseModel):
    user_description :str = Field(...,description="All what the user said about the question well redacted without mentioning the user.")
    bot_response:str = Field(..., description="Bot response.")
    finished :bool = Field(...,description="If the user says that the info is correct.")