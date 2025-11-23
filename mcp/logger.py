"""Hybrid Log Writer for MCP Tool Calls

This module logs MCP tool invocations in a hybrid format:
- Standard JSON-RPC request/response
- A2A-style metadata (timestamp, session, status, latency)

All logs are appended to logs/events.jsonl in JSONL format.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional


class MCPLogger:
    """Logger for MCP tool invocations with hybrid JSON-RPC + A2A format."""

    def __init__(self, log_dir: Path = Path("logs")):
        """Initialize MCP logger.

        Args:
            log_dir: Directory to store log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / "events.jsonl"

    def log_tool_call(
        self,
        session_id: str,
        request: Dict[str, Any],
        response: Dict[str, Any],
        latency_ms: float,
        actor: str = "ai_agent"
    ) -> str:
        """Log a single MCP tool call.

        Args:
            session_id: Session identifier
            request: JSON-RPC request object
            response: JSON-RPC response object
            latency_ms: Execution time in milliseconds
            actor: Actor performing the action (default: "ai_agent")

        Returns:
            str: Event ID of the logged event
        """
        event_id = f"evt-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).isoformat()

        # Determine status
        status = "error" if "error" in response else "success"

        # Create hybrid log entry
        event = {
            "event_id": event_id,
            "timestamp": timestamp,
            "session_id": session_id,
            "actor": actor,
            "channel": "mcp_tool",
            "jsonrpc_request": request,
            "jsonrpc_response": response,
            "status": status,
            "latency_ms": round(latency_ms, 2)
        }

        # Append to JSONL file
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

        return event_id

    def log_user_message(
        self,
        session_id: str,
        content: str,
        actor: str = "user"
    ) -> str:
        """Log a user message.

        Args:
            session_id: Session identifier
            content: Message content
            actor: Actor (default: "user")

        Returns:
            str: Event ID
        """
        event_id = f"evt-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).isoformat()

        event = {
            "event_id": event_id,
            "timestamp": timestamp,
            "session_id": session_id,
            "actor": actor,
            "channel": "chat",
            "event_type": "user_message",
            "content": content,
            "status": "success",
            "latency_ms": 0
        }

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

        return event_id

    def log_ai_message(
        self,
        session_id: str,
        content: str,
        actor: str = "ai_assistant"
    ) -> str:
        """Log an AI assistant message.

        Args:
            session_id: Session identifier
            content: Message content
            actor: Actor (default: "ai_assistant")

        Returns:
            str: Event ID
        """
        event_id = f"evt-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).isoformat()

        event = {
            "event_id": event_id,
            "timestamp": timestamp,
            "session_id": session_id,
            "actor": actor,
            "channel": "chat",
            "event_type": "ai_message",
            "content": content,
            "status": "success",
            "latency_ms": 0
        }

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

        return event_id

    def get_session_logs(
        self,
        session_id: str,
        event_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve all logs for a specific session.

        Args:
            session_id: Session identifier
            event_type: Optional filter by event type or channel

        Returns:
            List of log events for the session
        """
        logs = []

        if not self.log_file.exists():
            return logs

        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    event = json.loads(line.strip())
                    if event.get("session_id") == session_id:
                        # Apply optional filter
                        if event_type:
                            if (event.get("channel") == event_type or
                                event.get("event_type") == event_type):
                                logs.append(event)
                        else:
                            logs.append(event)
                except json.JSONDecodeError:
                    continue

        return logs

    def get_all_sessions(self) -> List[str]:
        """Get all unique session IDs from the log file.

        Returns:
            List of session IDs
        """
        sessions = set()

        if not self.log_file.exists():
            return []

        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    event = json.loads(line.strip())
                    if "session_id" in event:
                        sessions.add(event["session_id"])
                except json.JSONDecodeError:
                    continue

        return sorted(list(sessions))

    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with session statistics
        """
        logs = self.get_session_logs(session_id)

        if not logs:
            return {
                "session_id": session_id,
                "event_count": 0,
                "tool_calls": 0,
                "errors": 0,
                "total_latency_ms": 0
            }

        tool_calls = [log for log in logs if log.get("channel") == "mcp_tool"]
        errors = [log for log in logs if log.get("status") == "error"]
        total_latency = sum(log.get("latency_ms", 0) for log in logs)

        # Extract unique tools used
        tools_used = set()
        for log in tool_calls:
            req = log.get("jsonrpc_request", {})
            params = req.get("params", {})
            tool_name = params.get("name")
            if tool_name:
                tools_used.add(tool_name)

        return {
            "session_id": session_id,
            "event_count": len(logs),
            "tool_calls": len(tool_calls),
            "errors": len(errors),
            "total_latency_ms": round(total_latency, 2),
            "tools_used": sorted(list(tools_used)),
            "first_event": logs[0].get("timestamp") if logs else None,
            "last_event": logs[-1].get("timestamp") if logs else None
        }

    def clear_session_logs(self, session_id: str) -> int:
        """Clear all logs for a specific session.

        Args:
            session_id: Session identifier

        Returns:
            Number of events removed
        """
        if not self.log_file.exists():
            return 0

        # Read all events
        all_events = []
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    event = json.loads(line.strip())
                    all_events.append(event)
                except json.JSONDecodeError:
                    continue

        # Filter out session events
        filtered_events = [
            event for event in all_events
            if event.get("session_id") != session_id
        ]

        removed_count = len(all_events) - len(filtered_events)

        # Rewrite file
        with open(self.log_file, "w", encoding="utf-8") as f:
            for event in filtered_events:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")

        return removed_count

    def clear_all_logs(self) -> int:
        """Clear all logs.

        Returns:
            Number of events removed
        """
        if not self.log_file.exists():
            return 0

        # Count events
        count = 0
        with open(self.log_file, "r", encoding="utf-8") as f:
            count = sum(1 for _ in f)

        # Clear file
        self.log_file.unlink()

        return count


# Singleton instance
_logger_instance: Optional[MCPLogger] = None


def get_logger(log_dir: Path = Path("logs")) -> MCPLogger:
    """Get or create the global logger instance.

    Args:
        log_dir: Directory to store log files

    Returns:
        MCPLogger instance
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = MCPLogger(log_dir)
    return _logger_instance
