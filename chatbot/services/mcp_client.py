import json
import os
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

BASE_DIR = Path(__file__).resolve().parents[2]


class ProjectMCPClient:
    def __init__(self):
        self.server_params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "mcp_server.server"],
            env={
                **os.environ,
                "PYTHONPATH": str(BASE_DIR) + os.pathsep + os.environ.get("PYTHONPATH", ""),
            }
        )

    async def get_server_capabilities(self) -> dict:
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                resources = await session.list_resources()
                prompts = await session.list_prompts()
                return {
                    "tools": [x.name for x in tools.tools],
                    "resources": [str(x.uri) for x in resources.resources],
                    "prompts": [x.name for x in prompts.prompts],
                }

    async def execute(self, tool_name: str, arguments: dict, resource_uri: str, prompt_name: str) -> dict:
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                tools = await session.list_tools()
                resources = await session.list_resources()
                prompts = await session.list_prompts()

                if tool_name not in (x.name for x in tools.tools):
                    raise ValueError("Unknown MCP tool")
                if resource_uri not in (str(x.uri) for x in resources.resources):
                    raise ValueError("Unknown MCP resource")
                if prompt_name not in (x.name for x in prompts.prompts):
                    raise ValueError("Unknown MCP prompt")

                resource_text = None
                resource_response = await session.read_resource(resource_uri)
                for content_item in getattr(resource_response, "contents", []):
                    txt = getattr(content_item, "text", None)
                    if txt is not None:
                        resource_text = txt
                        break

                if resource_text is None or not isinstance(resource_text, (str, bytes, bytearray)):
                    raise RuntimeError("Resource contains no text")
                resource_data = json.loads(resource_text)

                prompt_response = await session.get_prompt(prompt_name)
                prompt_texts = []
                for msg in getattr(prompt_response, "messages", []):
                    content_obj = getattr(msg, "content", None)
                    if content_obj is not None:
                        txt = getattr(content_obj, "text", None)
                        if txt:
                            prompt_texts.append(txt)
                prompt_text = "\n".join(prompt_texts)

                tool_response = await session.call_tool(name=tool_name, arguments=arguments)

                is_error_flag = getattr(tool_response, "is_error", getattr(tool_response, "isError", False))
                if is_error_flag:
                    details_list = []
                    for item in getattr(tool_response, "content", []):
                        txt = getattr(item, "text", None)
                        if txt:
                            details_list.append(txt)
                    details = "".join(details_list)
                    raise ValueError(details or "MCP tool failed")

                result = getattr(tool_response, "structuredContent", None)
                if result is None:
                    raw_content = getattr(tool_response, "content", [])
                    raw = None
                    for item in raw_content:
                        txt = getattr(item, "text", None)
                        if txt is not None:
                            raw = txt
                            break

                    if raw is None or not isinstance(raw, (str, bytes, bytearray)):
                        raise RuntimeError("Tool returned no usable content")

                    try:
                        result = json.loads(raw)
                    except (TypeError, ValueError, json.JSONDecodeError):
                        result = {"result": raw}

                if isinstance(result, dict) and set(result) == {"result"} and isinstance(result["result"], dict):
                    result = result["result"]

                if not isinstance(result, dict):
                    raise RuntimeError("Tool result must be a JSON object")

                return {
                    "tool_result": result,
                    "resource": {"uri": resource_uri, "data": resource_data},
                    "prompt": {"name": prompt_name, "content": prompt_text},
                }