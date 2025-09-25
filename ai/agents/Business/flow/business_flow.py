from pydantic import BaseModel, Field

from ai.agents.Business.business_type import BusinessType


# 1. Define your structured schema with Pydantic (or JSON schema)
class BusinessFlowStructure(BaseModel):
    business_flow:[str] = Field(...,description="Workflow of tasks that the business has.")
    finished : bool = Field(..., description="Flag that tells that the client doesn't want to add or update anything more about the workflow.")