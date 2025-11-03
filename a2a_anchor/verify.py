"""
Verification Module for A2A Trace Anchoring

This module provides functions to verify the integrity of anchored traces
by following the verification chain:
1. Get memo from XRPL transaction
2. Retrieve trace from IPFS using CID
3. Recalculate Merkle Root
4. Compare with anchored Merkle Root
"""

from typing import Dict, Any, Optional
import json

from .ipfs_client import IPFSClient
from .xrpl_client import XRPLClient
from .merkle import compute_trace_merkle


class VerificationResult:
    """Result of trace verification."""

    def __init__(
        self,
        verified: bool,
        tx_hash: str,
        session_id: Optional[str] = None,
        cid: Optional[str] = None,
        expected_root: Optional[str] = None,
        computed_root: Optional[str] = None,
        error: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.verified = verified
        self.tx_hash = tx_hash
        self.session_id = session_id
        self.cid = cid
        self.expected_root = expected_root
        self.computed_root = computed_root
        self.error = error
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "verified": self.verified,
            "tx_hash": self.tx_hash,
            "session_id": self.session_id,
            "cid": self.cid,
            "expected_root": self.expected_root,
            "computed_root": self.computed_root,
            "match": self.expected_root == self.computed_root if self.expected_root and self.computed_root else None,
            "error": self.error,
            "details": self.details
        }

    def __str__(self) -> str:
        """String representation."""
        if self.verified:
            return f"✓ VERIFIED - Session: {self.session_id}, CID: {self.cid}"
        else:
            return f"✗ VERIFICATION FAILED - {self.error}"


def verify_trace(
    tx_hash: str,
    xrpl_client: XRPLClient,
    ipfs_client: IPFSClient
) -> VerificationResult:
    """
    Verify trace integrity from XRPL transaction hash.

    Verification flow:
    1. Retrieve transaction from XRPL
    2. Extract memo with CID and Merkle Root
    3. Retrieve trace JSON from IPFS using CID
    4. Recalculate Merkle Root from trace
    5. Compare with anchored Merkle Root

    Args:
        tx_hash: XRPL transaction hash
        xrpl_client: XRPL client instance
        ipfs_client: IPFS client instance

    Returns:
        VerificationResult object
    """
    try:
        # Step 1: Get transaction
        tx_data = xrpl_client.get_transaction(tx_hash)

        # Step 2: Extract memo
        memo_data = xrpl_client.get_memo_from_transaction(tx_hash)

        if not memo_data:
            return VerificationResult(
                verified=False,
                tx_hash=tx_hash,
                error="No memo found in transaction"
            )

        # Validate memo structure
        required_fields = ["cid", "root", "sid"]
        for field in required_fields:
            if field not in memo_data:
                return VerificationResult(
                    verified=False,
                    tx_hash=tx_hash,
                    error=f"Missing required field in memo: {field}"
                )

        cid = memo_data["cid"]
        expected_root = memo_data["root"]
        session_id = memo_data["sid"]

        # Step 3: Retrieve trace from IPFS
        try:
            trace_data = ipfs_client.get_json(cid)
        except Exception as e:
            return VerificationResult(
                verified=False,
                tx_hash=tx_hash,
                session_id=session_id,
                cid=cid,
                expected_root=expected_root,
                error=f"Failed to retrieve trace from IPFS: {e}"
            )

        # Step 4: Recalculate Merkle Root
        trace_json = json.dumps(trace_data, ensure_ascii=False, indent=2)
        computed_root, chunks = compute_trace_merkle(trace_json)

        # Step 5: Compare roots
        verified = expected_root == computed_root

        return VerificationResult(
            verified=verified,
            tx_hash=tx_hash,
            session_id=session_id,
            cid=cid,
            expected_root=expected_root,
            computed_root=computed_root,
            details={
                "model": memo_data.get("model"),
                "timestamp": memo_data.get("ts"),
                "version": memo_data.get("v"),
                "ledger_index": tx_data.get("ledger_index"),
                "chunks": len(chunks),
                "trace_events": len(trace_data.get("events", []))
            }
        )

    except Exception as e:
        return VerificationResult(
            verified=False,
            tx_hash=tx_hash,
            error=f"Verification failed: {e}"
        )


def verify_trace_from_cid(
    cid: str,
    expected_root: str,
    ipfs_client: IPFSClient
) -> VerificationResult:
    """
    Verify trace integrity from CID (without XRPL).

    This is useful for verifying traces that are only stored in IPFS
    without XRPL anchoring.

    Args:
        cid: IPFS Content Identifier
        expected_root: Expected Merkle Root
        ipfs_client: IPFS client instance

    Returns:
        VerificationResult object
    """
    try:
        # Retrieve trace from IPFS
        trace_data = ipfs_client.get_json(cid)

        # Recalculate Merkle Root
        trace_json = json.dumps(trace_data, ensure_ascii=False, indent=2)
        computed_root, chunks = compute_trace_merkle(trace_json)

        # Compare roots
        verified = expected_root == computed_root

        return VerificationResult(
            verified=verified,
            tx_hash="N/A",
            session_id=trace_data.get("session", {}).get("id"),
            cid=cid,
            expected_root=expected_root,
            computed_root=computed_root,
            details={
                "chunks": len(chunks),
                "trace_events": len(trace_data.get("events", []))
            }
        )

    except Exception as e:
        return VerificationResult(
            verified=False,
            tx_hash="N/A",
            cid=cid,
            expected_root=expected_root,
            error=f"Verification failed: {e}"
        )


def verify_trace_from_json(
    trace_json: str,
    expected_root: str
) -> VerificationResult:
    """
    Verify trace integrity from JSON string.

    Args:
        trace_json: Trace JSON string
        expected_root: Expected Merkle Root

    Returns:
        VerificationResult object
    """
    try:
        # Parse JSON
        trace_data = json.loads(trace_json)

        # Recalculate Merkle Root
        computed_root, chunks = compute_trace_merkle(trace_json)

        # Compare roots
        verified = expected_root == computed_root

        return VerificationResult(
            verified=verified,
            tx_hash="N/A",
            session_id=trace_data.get("session", {}).get("id"),
            cid="N/A",
            expected_root=expected_root,
            computed_root=computed_root,
            details={
                "chunks": len(chunks),
                "trace_events": len(trace_data.get("events", []))
            }
        )

    except Exception as e:
        return VerificationResult(
            verified=False,
            tx_hash="N/A",
            expected_root=expected_root,
            error=f"Verification failed: {e}"
        )


class TraceVerifier:
    """
    Convenience class for verifying traces with pre-configured clients.
    """

    def __init__(self, xrpl_client: XRPLClient, ipfs_client: IPFSClient):
        """
        Initialize verifier.

        Args:
            xrpl_client: XRPL client instance
            ipfs_client: IPFS client instance
        """
        self.xrpl = xrpl_client
        self.ipfs = ipfs_client

    def verify(self, tx_hash: str) -> VerificationResult:
        """
        Verify trace from transaction hash.

        Args:
            tx_hash: XRPL transaction hash

        Returns:
            VerificationResult object
        """
        return verify_trace(tx_hash, self.xrpl, self.ipfs)

    def verify_cid(self, cid: str, expected_root: str) -> VerificationResult:
        """
        Verify trace from CID.

        Args:
            cid: IPFS Content Identifier
            expected_root: Expected Merkle Root

        Returns:
            VerificationResult object
        """
        return verify_trace_from_cid(cid, expected_root, self.ipfs)

    def close(self) -> None:
        """Close client connections."""
        self.xrpl.close()
        self.ipfs.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
