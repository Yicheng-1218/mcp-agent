import shutil
import json
from pathlib import Path
from typing import Dict, Optional, Union, Any
from .utils.path import validate_file
from .types import MCPServer
from pydantic_ai.mcp import MCPServerStdio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from loguru import logger
from datetime import timedelta
import asyncio
import traceback
DEFAULT_CONFIG_PATH = "mcp_servers.json"


class ServerRegistry:
    """MCP Server Manager for managing server files."""

    def __init__(self, config_path: str | Path = DEFAULT_CONFIG_PATH) -> None:
        """Initialize the MCP Server Manager."""
        try:
            config_path = validate_file(config_path, ".json")
        except ValueError:
            logger.error(
                f"MCPSM: File '{config_path}' does not exist, or is not a json file."
            )
            raise ValueError(
                f"MCPSM: File '{config_path}' does not exist, or is not a json file."
            )

        self.config: Dict[str, Union[str, dict]] = json.loads(
            config_path.read_text(encoding="utf-8")
        )

        self.servers: Dict[str, MCPServer] = {}

        self.npx_available = self._detect_runtime("npx")
        self.uvx_available = self._detect_runtime("uvx")
        self.node_available = self._detect_runtime("node")

        # self.load_servers()
    async def initialize(self) -> None:
        """初始化伺服器註冊表"""
        await self.load_servers()

    def _detect_runtime(self, target: str) -> bool:
        """Check if a runtime is available in the system PATH."""
        founded = shutil.which(target)
        return True if founded else False

    async def _check_server_availability(self, server: MCPServer, timeout: int = 5) -> bool:
        """檢查單一伺服器是否可用"""
        try:
            if not server:
                return False
            
            server_params = StdioServerParameters(
                command=server.command,
                args=server.args,
                env=server.env,
            )
            if not isinstance(timeout,timedelta):
                timeout = timedelta(seconds=timeout)
                async with stdio_client(server_params) as (read, write):
                    async with ClientSession(read, write, read_timeout_seconds=timeout) as session:
                            await session.initialize()
                            await session.list_tools()
                            return True
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.warning(f"MCPC: Failed to connect to server '{server.name}': {e}")
            return False
    
    async def load_servers(self) -> None:
        """Load servers from the config file."""
        servers_config: Dict[str, Dict[str, Any]] = self.config.get("mcp_servers", {})
        if servers_config == {}:
            logger.warning("MCPSM: No servers found in the config file.")
            return

        for server_name, server_details in servers_config.items():
            try:
                if "command" not in server_details or "args" not in server_details:
                    logger.warning(
                        f"MCPSM: Invalid server details for '{server_name}'. Ignoring."
                    )
                    continue

                command = server_details["command"]
                if command == "npx":
                    if not self.npx_available:
                        logger.warning(
                            f"MCPSM: npx is not available. Cannot load server '{server_name}'."
                        )
                        continue
                elif command == "uvx":
                    if not self.uvx_available:
                        logger.warning(
                            f"MCPSM: uvx is not available. Cannot load server '{server_name}'."
                        )
                        continue
                elif command == "node":
                    if not self.node_available:
                        logger.warning(
                            f"MCPSM: node is not available. Cannot load server '{server_name}'."
                        )
                        continue

                mcp_server = MCPServer(
                    name=server_name,
                    command=command,
                    args=server_details["args"],
                    env=server_details.get("env", None),
                    timeout=server_details.get("timeout", None),
                )
                
                if await self._check_server_availability(mcp_server):
                    self.servers[server_name] = mcp_server
                    logger.debug(f"MCPSM: Loaded server: '{server_name}'.")
                else:
                    logger.warning(f"MCPSM: Server '{server_name}' is not available. Ignoring.")
                    
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.warning(f"MCPSM: Error processing server '{server_name}': {e}")
                continue

    def remove_server(self, server_name: str) -> None:
        """Remove a server from the available servers."""
        try:
            self.servers.pop(server_name)
            logger.info(f"MCPSM: Removed server: {server_name}")
        except KeyError:
            logger.warning(f"MCPSM: Server '{server_name}' not found. Cannot remove.")

    def get_server(self, server_name: str) -> Optional[MCPServer]:
        """Get the server by name."""
        return self.servers.get(server_name, None)
    
    def get_all_servers(self):
        """Get all available servers."""
        # return self.servers
        return [MCPServerStdio(command=server.command, args=server.args, env=server.env) for server in self.servers.values()]
