"""MCP Client - Tool Invocation with Logging

This module provides a client for calling MCP tools via JSON-RPC
and logging all interactions.
"""

import time
import requests
from typing import Dict, Any, List, Optional
from .logger import MCPLogger


class MCPClient:
    """Client for MCP server communication with automatic logging."""

    def __init__(
        self,
        server_url: str = "http://localhost:8000",
        logger: Optional[MCPLogger] = None,
        timeout: int = 30
    ):
        """Initialize MCP client.

        Args:
            server_url: URL of the MCP server
            logger: Logger instance (will create one if not provided)
            timeout: Request timeout in seconds
        """
        self.server_url = server_url
        self.logger = logger or MCPLogger()
        self.timeout = timeout
        self._request_id = 0

    def _get_next_request_id(self) -> int:
        """Get next request ID."""
        self._request_id += 1
        return self._request_id

    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools from the server.

        Returns:
            List of tool definitions

        Raises:
            Exception: If server request fails
        """
        request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": self._get_next_request_id()
        }

        try:
            response = requests.post(
                self.server_url,
                json=request,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                raise Exception(f"Server error: {data['error']}")

            return data.get("result", {}).get("tools", [])

        except requests.RequestException as e:
            raise Exception(f"Failed to list tools: {str(e)}")

    def call_tool(
        self,
        session_id: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call a tool on the MCP server.

        This method automatically logs the request and response.

        Args:
            session_id: Session identifier for logging
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool result dictionary

        Raises:
            Exception: If tool call fails
        """
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": self._get_next_request_id()
        }

        # Measure latency
        start_time = time.time()

        try:
            response = requests.post(
                self.server_url,
                json=request,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            response.raise_for_status()
            response_data = response.json()

        except requests.RequestException as e:
            # Log error response
            latency_ms = (time.time() - start_time) * 1000
            error_response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32000,
                    "message": str(e)
                },
                "id": request["id"]
            }

            self.logger.log_tool_call(
                session_id=session_id,
                request=request,
                response=error_response,
                latency_ms=latency_ms
            )

            raise Exception(f"Failed to call tool '{tool_name}': {str(e)}")

        latency_ms = (time.time() - start_time) * 1000

        # Log successful call
        self.logger.log_tool_call(
            session_id=session_id,
            request=request,
            response=response_data,
            latency_ms=latency_ms
        )

        # Check for server error
        if "error" in response_data:
            raise Exception(f"Tool error: {response_data['error']}")

        return response_data.get("result", {})

    def call_tool_simple(
        self,
        session_id: str,
        tool_name: str,
        **kwargs
    ) -> str:
        """Call a tool and return text result.

        This is a simplified wrapper that returns the text content directly.

        Args:
            session_id: Session identifier
            tool_name: Tool name
            **kwargs: Tool arguments

        Returns:
            Text result from the tool

        Raises:
            Exception: If tool call fails
        """
        result = self.call_tool(session_id, tool_name, kwargs)

        # Extract text from content
        content = result.get("content", [])
        if content and isinstance(content, list):
            return content[0].get("text", "")

        return ""

    def health_check(self) -> bool:
        """Check if the MCP server is healthy.

        Returns:
            True if server is healthy, False otherwise
        """
        try:
            response = requests.get(
                f"{self.server_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except requests.RequestException:
            return False


class MCPToolkit:
    """High-level toolkit for using MCP tools with simplified interface."""

    def __init__(self, client: MCPClient, session_id: str):
        """Initialize toolkit.

        Args:
            client: MCP client instance
            session_id: Session identifier
        """
        self.client = client
        self.session_id = session_id
        self._tools_cache: Optional[List[Dict[str, Any]]] = None

    def get_available_tools(self) -> List[str]:
        """Get list of available tool names.

        Returns:
            List of tool names
        """
        if self._tools_cache is None:
            self._tools_cache = self.client.list_tools()

        return [tool["name"] for tool in self._tools_cache]

    def calculate(self, expression: str) -> str:
        """Calculate a mathematical expression.

        Args:
            expression: Math expression to evaluate

        Returns:
            Result as string
        """
        return self.client.call_tool_simple(
            self.session_id,
            "calculate",
            expression=expression
        )

    def get_time(self) -> str:
        """Get current time.

        Returns:
            Current time in ISO format
        """
        return self.client.call_tool_simple(
            self.session_id,
            "get_current_time"
        )

    def count_words(self, text: str) -> str:
        """Count words in text.

        Args:
            text: Text to count words in

        Returns:
            Word count as string
        """
        return self.client.call_tool_simple(
            self.session_id,
            "count_words",
            text=text
        )

    def reverse_string(self, text: str) -> str:
        """Reverse a string.

        Args:
            text: Text to reverse

        Returns:
            Reversed text
        """
        return self.client.call_tool_simple(
            self.session_id,
            "reverse_string",
            text=text
        )

    def check_palindrome(self, text: str) -> str:
        """Check if text is a palindrome.

        Args:
            text: Text to check

        Returns:
            Result message
        """
        return self.client.call_tool_simple(
            self.session_id,
            "check_palindrome",
            text=text
        )
