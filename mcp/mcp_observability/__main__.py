"""Entry point for the observability MCP server."""

from mcp_observability.server import main

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
