from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

async def call_mcp_tool(tool_name: str, arguments: dict):
    server_params = StdioServerParameters(
        command="python",          # or path to your MCP server
        args=[r"D:\\Projetcs\\Python\\mcp-python\\main.py"],   # your MCP server script
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return result