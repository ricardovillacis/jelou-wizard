import asyncio
import json
import os
from typing import Dict, Any, List, Optional
from mcp_use import MCPAgent, MCPClient
from langchain_anthropic import ChatAnthropic

from ai.agents.jelouai.jelou_response_structure import PackageInfoStructure

import logging
logging.getLogger("mcp_use").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.CRITICAL)

class JelouMCP():
    
    def __init__(self):
        # Initialize Anthropic client
        jelou_mcp_url = os.getenv('JELOU_MCP_URL')
        if not jelou_mcp_url:
            raise ValueError("JELOU_MCP_URL environment variable is required")
        config = {"mcpServers": {"http": {"url": jelou_mcp_url}}}
        mcp_client = MCPClient.from_dict(config)
        llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.mcp_agent = MCPAgent(llm=llm,client=mcp_client)
    
    
    async def get_package_info(self, package_use: str) -> PackageInfoStructure:
        """Search workflow packages via MCP and return structured info.
        Uses tool 'search-workflow-packages' and extracts workflow syntax, inputs, and usage.
        """
        result = await self.mcp_agent.run(f"Search for Jelou package about {package_use} and bring information of it.",output_schema=PackageInfoStructure)        
        return result
        