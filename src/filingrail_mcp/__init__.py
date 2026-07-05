"""filingrail-mcp — MCP server exposing the Filingrail SEC EDGAR API as tools.

For Claude Desktop / Cursor / Continue / any MCP-compatible agent.
"""

from filingrail_mcp.server import mcp, main

__version__ = "0.1.1"
__all__ = ["mcp", "main", "__version__"]
