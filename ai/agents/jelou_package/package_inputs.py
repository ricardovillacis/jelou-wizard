from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List



class PackageInputsStructure(BaseModel):
    """Structured information about a workflow package."""
    package_name: str = Field(..., description="Package name")
    package_inputs: str = Field(description="Inputs list with name, type, and description")
    package_outputs: str = Field(description="Output lists with name, type and description")
    all_inputs_filled: bool = Field(description="If all inputs are filled")
    user_confirmed: bool = Field(description="If the user confirmed the inputs after filling them")
    bot_response: str = Field(description="Bot response")
    updated_slots: Dict[str, str] = Field(...,description="Inputs name as key and input values as values(full inputs text, don't simplified it)given by the user.")