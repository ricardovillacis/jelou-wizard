from pydantic import BaseModel, Field

from ai.agents.Business.business_type import BusinessType


# 1. Define your structured schema with Pydantic (or JSON schema)
class BusinessInfoStructure(BaseModel):
    business_type:BusinessType = Field(...,description="Type of business that the user wants to create the agent for.")
    reasoning:str = Field(..., description="Reasoning of why you choose that business type.")