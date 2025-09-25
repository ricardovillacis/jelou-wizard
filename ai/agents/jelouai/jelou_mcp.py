import asyncio
import json
from typing import Dict, Any, List, Optional
from mcp.client.session import ClientSession
from ai.agents.jelouai.package_info_structure import PackageInfoStructure


class JelouMCP():
    
    def __init__(self, mcp_server_config: Optional[Dict[str, Any]] = None):
        self.mcp_session: Optional[ClientSession] = None
        self.mcp_tools: List[Dict[str, Any]] = []
        self.mcp_server_config = mcp_server_config
        self._initialization_task: Optional[asyncio.Task] = None
        
        # Initialize MCP if configuration provided
        if mcp_server_config:
            self._initialization_task = asyncio.create_task(self._initialize_mcp(mcp_server_config))

    
    async def _initialize_mcp(self, config: Dict[str, Any]) -> None:
        """Initialize MCP connection with the specified server."""
        try:
            
            transport = HttpClientTransport("http://localhost:3000/mcp")
            async with socket_client(url) as (read, write):
                async with ClientSession(read, write) as session:
                    self.mcp_session = session
                    await self._load_mcp_tools()
                    
        except Exception as e:
            print(f"Failed to initialize MCP: {e}")
            self.mcp_session = None
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool with the given arguments."""
        if not self.mcp_session:
            return {"error": "MCP session not initialized"}
        
        try:
            result = await self.mcp_session.call_tool(tool_name, arguments)
            return result
        except Exception as e:
            return {"error": f"Failed to call MCP tool {tool_name}: {e}"}
    
    def get_available_tools(self) -> List[str]:
        """Get list of available MCP tool names."""
        return [tool.name for tool in self.mcp_tools]
    
    async def wait_for_initialization(self) -> None:
        """Wait for MCP initialization to complete."""
        if self._initialization_task:
            await self._initialization_task
            self._initialization_task = None
    
    async def get_package_info(self, package_name: str) -> PackageInfoStructure:
        """Search workflow packages via MCP and return structured info.
        Uses tool 'search-workflow-packages' and extracts workflow syntax, inputs, and usage.
        """
        # Wait for initialization to complete
        await self.wait_for_initialization()
        
        if not self.mcp_session:
            raise RuntimeError("MCP session not initialized. Provide mcp_server_config when creating JelouAgent.")
        
        raw = await self.call_mcp_tool("search-workflow-packages", {"query": package_name})
        # Expecting the tool to return a JSON text or dict with keys we need
        data: Dict[str, Any]
        if isinstance(raw, dict) and "results" in raw:
            data = raw
        else:
            try:
                data = json.loads(raw) if isinstance(raw, str) else raw
            except Exception:
                data = {"results": []}
        
        # Normalize and pick best match
        results = data.get("results", []) or []
        best = results[0] if results else {}
        
        # Extract fields
        workflow_syntax = best.get("workflow_syntax") or best.get("syntax") or ""
        inputs = best.get("inputs") or []
        usage = best.get("usage") or best.get("readme_usage") or ""
        name = best.get("name") or package_name
        version = best.get("version")
        homepage = best.get("homepage") or best.get("docs")
        source = best.get("source") or best.get("repository")
        
        # Ensure inputs have a normalized structure
        normalized_inputs: List[Dict[str, Any]] = []
        for item in inputs:
            if isinstance(item, dict):
                normalized_inputs.append({
                    "name": item.get("name") or item.get("id") or "input",
                    "type": item.get("type") or item.get("datatype") or "string",
                    "description": item.get("description") or ""
                })
            else:
                normalized_inputs.append({
                    "name": str(item),
                    "type": "string",
                    "description": ""
                })
        
        return PackageInfoStructure(
            name=name,
            version=version,
            workflow_syntax=workflow_syntax,
            inputs=normalized_inputs,
            usage=usage,
            homepage=homepage,
            source=source,
        )
    
    async def send_message_with_mcp(self, content: str, max_tokens: int = 1000) -> Any:
        """Send a message and get response, potentially using MCP tools."""
        # Add user message
        self.add_user_message(content)
        
        # Check if we should use MCP tools based on the message content
        should_use_mcp = self._should_use_mcp_tools(content)
        
        if should_use_mcp and self.mcp_tools:
            # Use MCP-enhanced response
            return await self._send_with_mcp_enhancement(content, max_tokens)
        else:
            # Use standard response
            return self.send_message(content, max_tokens)
    
    def get_model_assistant_message(self, model_response):
        """Extract the assistant message from the model response."""
        if hasattr(model_response, 'assistant_message'):
            return model_response.assistant_message
        elif hasattr(model_response, 'response'):
            return model_response.response
        else:
            return str(model_response)
    
    async def close_mcp_session(self):
        """Close the MCP session."""
        if self.mcp_session:
            await self.mcp_session.close()
            self.mcp_session = None
