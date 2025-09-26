from pydantic import BaseModel, Field

from ai.agents.Business.business_type import BusinessType


# 1. Define your structured schema with Pydantic (or JSON schema)
class EBusinessWorkflowStructure(BaseModel):
    bot_response:str =Field(...,description="bot_response with business workflow so far.")
    buisiness_workflow:str = Field(...,description="Business workflow")
    user_confirmed: bool = Field(description="If the user confirmed that the business workflow is correct")
