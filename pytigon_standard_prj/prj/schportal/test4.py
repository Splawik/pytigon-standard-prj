import asyncio
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

async def main():
    async with streamablehttp_client("http://127.0.0.1:8000/mcp") as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            
            # Lista narzędzi
            tools = await session.list_tools()
            print("TOOLS:", tools)
            
            # Lista zasobów
            resources = await session.list_resources()
            print("RESOURCES:", resources)

if __name__ == "__main__":
    asyncio.run(main())
