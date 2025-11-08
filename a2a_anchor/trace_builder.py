"""Build A2A Trace from LangChain agent execution results"""

from datetime import datetime, timezone
from typing import Dict, List, Any
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from .trace_schema import (
    TraceJSON, Session, Model, Event, Usage, Hashing
)
from .merkle import compute_trace_merkle


class TraceBuilder:
    """Build A2A trace from LangChain messages"""

    def __init__(self, session_id: str = None):
        self.session_id = session_id or self._generate_session_id()
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.events: List[Event] = []
        self.usage_data: List[Usage] = []
        self.actors = set(["user", "assistant"])
        self.model_info = None

    @staticmethod
    def _generate_session_id() -> str:
        """Generate a session ID"""
        import uuid
        return f"session-{uuid.uuid4().hex[:12]}"

    def add_message(self, message) -> None:
        """Add a message to the trace"""
        timestamp = datetime.now(timezone.utc).isoformat()

        if isinstance(message, HumanMessage):
            event = Event(
                type="human_message",
                ts=timestamp,
                content=message.content
            )
            self.events.append(event)

        elif isinstance(message, AIMessage):
            # Extract model info if available
            if hasattr(message, 'response_metadata') and message.response_metadata:
                metadata = message.response_metadata
                if 'model_name' in metadata and not self.model_info:
                    self.model_info = Model(
                        name=metadata['model_name'],
                        provider=metadata.get('model_provider', 'unknown')
                    )

                # Extract usage info
                if 'token_usage' in metadata:
                    usage = metadata['token_usage']
                    self.usage_data.append(Usage(
                        turn=len(self.usage_data) + 1,
                        input_tokens=usage.get('prompt_tokens', 0),
                        output_tokens=usage.get('completion_tokens', 0)
                    ))

            # Handle tool calls
            if hasattr(message, 'tool_calls') and message.tool_calls:
                for tool_call in message.tool_calls:
                    tool_name = tool_call.get('name', 'unknown')
                    self.actors.add(f"tool:{tool_name}")

                    event = Event(
                        type="ai_tool_call",
                        ts=timestamp,
                        tool=tool_name,
                        args=tool_call.get('args', {}),
                        tool_call_id=tool_call.get('id')
                    )
                    self.events.append(event)

            # Regular AI message
            if message.content:
                event = Event(
                    type="ai_message",
                    ts=timestamp,
                    content=message.content
                )
                self.events.append(event)

        elif isinstance(message, ToolMessage):
            tool_name = message.name if hasattr(message, 'name') else 'unknown'
            self.actors.add(f"tool:{tool_name}")

            event = Event(
                type="tool_result",
                ts=timestamp,
                tool=tool_name,
                content=message.content,
                tool_call_id=message.tool_call_id if hasattr(message, 'tool_call_id') else None
            )
            self.events.append(event)

    def add_messages(self, messages: List) -> None:
        """Add multiple messages"""
        for msg in messages:
            self.add_message(msg)

    def build(self, compute_merkle: bool = True) -> TraceJSON:
        """
        Build the final TraceJSON

        Args:
            compute_merkle: Whether to compute Merkle root

        Returns:
            TraceJSON object
        """
        # Default model if not extracted
        if not self.model_info:
            self.model_info = Model(name="unknown", provider="unknown")

        # Create session
        session = Session(
            id=self.session_id,
            createdAt=self.created_at,
            actors=sorted(list(self.actors))
        )

        # Create trace
        trace = TraceJSON(
            session=session,
            model=self.model_info,
            events=self.events,
            usage=self.usage_data
        )

        # Compute Merkle root if requested
        if compute_merkle:
            # Capture the JSON used for merkle calculation
            trace_json = trace.to_json()
            merkle_root, chunk_hashes = compute_trace_merkle(trace_json)

            # Store the JSON used for merkle calculation
            trace._merkle_json_cache = trace_json

            # Update hashing field
            trace.hashing.chunkMerkleRoot = merkle_root
            trace.hashing.chunks = chunk_hashes

        return trace

    @staticmethod
    def from_langchain_result(result: Dict[str, Any], session_id: str = None) -> TraceJSON:
        """
        Build trace from LangChain agent result

        Args:
            result: Result dict from agent.invoke()
            session_id: Optional session ID

        Returns:
            TraceJSON object
        """
        builder = TraceBuilder(session_id)

        if 'messages' in result:
            builder.add_messages(result['messages'])

        return builder.build()
