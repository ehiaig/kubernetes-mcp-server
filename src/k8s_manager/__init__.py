from .server import main
import asyncio

def start():
    """MCP Fetch Server - HTTP fetching functionality for MCP"""
    asyncio.run(main())

__all__ = ["start", "main"]