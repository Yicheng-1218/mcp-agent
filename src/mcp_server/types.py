from dataclasses import dataclass, field
from datetime import timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path


@dataclass
class MCPServer:
    """Class representing a MCP Server

    Args:
        name (str): Name of the server.
        command (str): Command to run the server.
        args (List[str], optional): Arguments for the command. Defaults to an empty list.
        env (Optional[Dict[str, str]], optional): Environment variables for the command. Defaults to None.
        timeout (Optional[timedelta], optional): Timeout for the command. Defaults to 10 seconds.
    """

    name: str
    command: str
    args: List[str] = field(default_factory=list)
    env: Optional[Dict[str, str]] = None
    timeout: Optional[timedelta] = timedelta(seconds=30)
    description: str = "No description available."