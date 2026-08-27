"""
OpenAI Codex / Function Calling schemas and dispatcher.
"""

import json
from typing import Dict, Any, List
from .mcp_server import TOOLS_METADATA, MCPServer

def get_openai_tools() -> List[Dict[str, Any]]:
    """Converts MCP tools metadata to OpenAI function format."""
    openai_tools = []
    for tool in TOOLS_METADATA:
        openai_tools.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["inputSchema"]
            }
        })
    return openai_tools

class OpenAIToolDispatcher:
    """Dispatches OpenAI tool calls to the underlying engine."""

    def __init__(self):
        self.server = MCPServer()

    def dispatch(self, tool_name: str, arguments_json: str) -> Dict[str, Any]:
        args = json.loads(arguments_json) if isinstance(arguments_json, str) else arguments_json
        return self.server.handle_call_tool(tool_name, args)
