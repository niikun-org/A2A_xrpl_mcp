"""A2A Trace JSON Schema Definition (a2a-0.1)"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class Session(BaseModel):
    """Session metadata"""
    id: str
    createdAt: str
    actors: List[str]


class Model(BaseModel):
    """Model information"""
    name: str
    provider: str


class Event(BaseModel):
    """Base event structure"""
    type: Literal["human_message", "ai_message", "ai_tool_call", "tool_result"]
    ts: str
    content: Optional[str] = None
    tool: Optional[str] = None
    args: Optional[Dict[str, Any]] = None
    tool_call_id: Optional[str] = None


class Usage(BaseModel):
    """Token usage per turn"""
    turn: int
    input_tokens: int
    output_tokens: int


class Hashing(BaseModel):
    """Hashing and Merkle tree information"""
    algorithm: str = "sha256"
    chunk_size: int = 4096
    chunkMerkleRoot: Optional[str] = None
    chunks: List[str] = Field(default_factory=list)


class Signature(BaseModel):
    """Digital signature"""
    actor: str
    address: str
    spec: str = "EIP-191-like"
    signature: Optional[str] = None


class Redaction(BaseModel):
    """Redaction policy"""
    policy: str = "pii_mask"
    masked_fields: List[str] = Field(default_factory=list)


class TraceJSON(BaseModel):
    """Complete A2A Trace JSON structure (a2a-0.1)"""
    traceVersion: str = "a2a-0.1"
    session: Session
    model: Model
    events: List[Event]
    usage: List[Usage] = Field(default_factory=list)
    hashing: Hashing = Field(default_factory=Hashing)
    signatures: List[Signature] = Field(default_factory=list)
    redactions: Redaction = Field(default_factory=Redaction)

    # Cache for the JSON used in Merkle Root calculation
    # This is NOT part of the A2A schema, just for internal use
    model_config = {"extra": "allow"}
    _merkle_json_cache: str = ""

    def to_json(self, **kwargs) -> str:
        """Export to JSON string"""
        return self.model_dump_json(indent=2, **kwargs)

    def get_merkle_json(self) -> str:
        """
        Get the JSON string that was used for Merkle Root calculation.
        This is the cached version without hashing/signatures/redactions fields populated.
        """
        return self._merkle_json_cache if self._merkle_json_cache else self.to_json()
