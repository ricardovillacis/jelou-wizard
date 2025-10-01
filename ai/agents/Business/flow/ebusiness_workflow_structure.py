from pydantic import BaseModel, Field

from ai.agents.Business.business_type import BusinessType


# 1. Define your structured schema with Pydantic (or JSON schema)
class EBusinessWorkflowStructure(BaseModel):
    bot_response:str =Field(...,description="Worfklow and bot response, never say the show the workflow in this message.")
    user_want_workflow:str = Field(..., description="If the user at the instant says that wants to see the workflow(ignore past user petitions to see the workflow)")
    business_workflow:str = Field(...,description="Business workflow")
    user_confirmed: bool = Field(description="If the user confirmed or says that the business workflow is correct")
