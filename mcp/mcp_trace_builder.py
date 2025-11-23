"""MCP Trace Builder - Convert JSON-RPC Logs to A2A Format

This module converts MCP tool invocation logs (JSON-RPC format)
to A2A trace format with Merkle Root verification.
"""

from typing import List, Dict, Any
from datetime import datetime

import sys
from pathlib import Path

# Add parent directory to path for importing a2a_anchor
sys.path.insert(0, str(Path(__file__).parent.parent))

from a2a_anchor.trace_schema import TraceJSON, Session, Model, Event, Usage, Hashing
from a2a_anchor.merkle import compute_trace_merkle


class MCPTraceBuilder:
    """Build A2A traces from MCP JSON-RPC logs."""

    @staticmethod
    def from_jsonl_logs(
        logs: List[Dict[str, Any]],
        model_name: str = "claude-3-5-sonnet-20241022",
        provider: str = "anthropic"
    ) -> TraceJSON:
        """Build A2A trace from JSONL log entries.

        Args:
            logs: List of log events from logger
            model_name: LLM model name used
            provider: LLM provider name

        Returns:
            TraceJSON object with Merkle Root computed

        Raises:
            ValueError: If logs are empty or invalid
        """
        if not logs:
            raise ValueError("No logs provided")

        # Extract session metadata
        session_id = logs[0].get("session_id")
        if not session_id:
            raise ValueError("Missing session_id in logs")

        created_at = logs[0].get("timestamp")

        # Collect unique actors
        actors = set(["user", "assistant"])  # Default actors

        # Build events list
        events: List[Event] = []

        for log in logs:
            timestamp = log.get("timestamp")
            channel = log.get("channel")
            event_type = log.get("event_type")

            # User message
            if event_type == "user_message":
                events.append(Event(
                    type="human_message",
                    ts=timestamp,
                    content=log.get("content", "")
                ))

            # AI message
            elif event_type == "ai_message":
                events.append(Event(
                    type="ai_message",
                    ts=timestamp,
                    content=log.get("content", "")
                ))

            # MCP tool call
            elif channel == "mcp_tool":
                request = log.get("jsonrpc_request", {})
                response = log.get("jsonrpc_response", {})

                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                tool_call_id = str(request.get("id", ""))

                # Add tool actor
                if tool_name:
                    actors.add(f"tool:{tool_name}")

                # Tool call event
                events.append(Event(
                    type="ai_tool_call",
                    ts=timestamp,
                    tool=tool_name,
                    args=arguments,
                    tool_call_id=tool_call_id
                ))

                # Tool result event
                result = response.get("result", {})
                error = response.get("error")

                if error:
                    # Error result
                    content = f"Error: {error.get('message', 'Unknown error')}"
                else:
                    # Success result
                    result_content = result.get("content", [])
                    if result_content and isinstance(result_content, list):
                        content = result_content[0].get("text", "")
                    else:
                        content = str(result)

                events.append(Event(
                    type="tool_result",
                    ts=timestamp,
                    tool_call_id=tool_call_id,
                    content=content
                ))

        # Build trace without hashing first
        trace = TraceJSON(
            session=Session(
                id=session_id,
                createdAt=created_at,
                actors=sorted(list(actors))
            ),
            model=Model(
                name=model_name,
                provider=provider
            ),
            events=events,
            usage=[],  # Token usage not available from MCP logs
            hashing=Hashing()
        )

        # Compute Merkle Root
        # Convert to JSON (without hashing fields populated)
        trace_json = trace.model_dump_json(
            indent=2,
            exclude={"hashing": {"chunkMerkleRoot", "chunks"}}
        )

        merkle_root, chunk_hashes = compute_trace_merkle(trace_json)

        # Update hashing information
        trace.hashing.chunkMerkleRoot = merkle_root
        trace.hashing.chunks = chunk_hashes

        # Cache the JSON for later verification
        trace._merkle_json_cache = trace_json

        return trace

    @staticmethod
    def from_session_file(
        log_file: Path,
        session_id: str,
        model_name: str = "claude-3-5-sonnet-20241022",
        provider: str = "anthropic"
    ) -> TraceJSON:
        """Build trace from a session in a JSONL log file.

        Args:
            log_file: Path to events.jsonl file
            session_id: Session ID to extract
            model_name: LLM model name
            provider: LLM provider

        Returns:
            TraceJSON object

        Raises:
            FileNotFoundError: If log file doesn't exist
            ValueError: If session not found
        """
        import json

        if not log_file.exists():
            raise FileNotFoundError(f"Log file not found: {log_file}")

        # Read all events for session
        session_logs = []

        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    event = json.loads(line.strip())
                    if event.get("session_id") == session_id:
                        session_logs.append(event)
                except json.JSONDecodeError:
                    continue

        if not session_logs:
            raise ValueError(f"No logs found for session: {session_id}")

        return MCPTraceBuilder.from_jsonl_logs(
            session_logs,
            model_name=model_name,
            provider=provider
        )

    @staticmethod
    def get_session_summary(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get summary statistics for a session's logs.

        Args:
            logs: List of log events

        Returns:
            Dictionary with summary statistics
        """
        if not logs:
            return {
                "event_count": 0,
                "tool_calls": 0,
                "errors": 0,
                "tools_used": []
            }

        tool_calls = []
        errors = []
        tools_used = set()

        for log in logs:
            if log.get("channel") == "mcp_tool":
                tool_calls.append(log)

                # Extract tool name
                request = log.get("jsonrpc_request", {})
                params = request.get("params", {})
                tool_name = params.get("name")
                if tool_name:
                    tools_used.add(tool_name)

                # Check for errors
                response = log.get("jsonrpc_response", {})
                if "error" in response or log.get("status") == "error":
                    errors.append(log)

        return {
            "session_id": logs[0].get("session_id"),
            "event_count": len(logs),
            "tool_calls": len(tool_calls),
            "errors": len(errors),
            "tools_used": sorted(list(tools_used)),
            "first_event": logs[0].get("timestamp"),
            "last_event": logs[-1].get("timestamp")
        }
