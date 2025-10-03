from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List



class PackageInfoStructure(BaseModel):
    """Structured information about a workflow package."""
    name: str = Field(..., description="Package name")
    version: Optional[str] = Field(default=None, description="Package version, if known")
    workflow_syntax: str = Field(..., description="Workflow syntax snippet or DSL")
    inputs: List[Dict[str, Any]] = Field(default_factory=list, description="Inputs list with name, type, description and if they are required or not.")
    outputs: List[Dict[str,Any]] = Field(default_factory=list,description="Outputs list with name, type, and description")
    usage: str = Field(..., description="Why is it used for")
    homepage: Optional[str] = Field(default=None, description="Homepage or documentation URL")
    source: Optional[str] = Field(default=None, description="Source repository or registry link")
