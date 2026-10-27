import asyncio
import json
from chatbot.services.mcp_client import ProjectMCPClient


async def main():
    client = ProjectMCPClient()
    print("Capabilities:")
    print(json.dumps(await client.get_server_capabilities(), indent=2))

    print("\nTesting PERT Tool Execution:")
    result = await client.execute(
        tool_name="pert_tool",
        arguments={"optimistic": 2.0, "most_likely": 5.0, "pessimistic": 14.0},
        resource_uri="project://pert/formula-rules",
        prompt_name="pert_assistant_prompt",
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())