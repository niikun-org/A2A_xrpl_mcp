"""
Anchor Service - Complete A2A Trace Anchoring Flow

This module integrates IPFS and XRPL clients to provide a complete
trace anchoring service.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import json

from .trace_schema import TraceJSON
from .ipfs_client import IPFSClient
from .xrpl_client import XRPLClient


class AnchorService:
    """
    Complete service for anchoring A2A traces to IPFS + XRPL.

    This service:
    1. Uploads trace JSON to IPFS
    2. Gets CID (Content Identifier)
    3. Anchors CID + Merkle Root to XRPL Memo
    4. Returns anchoring result with all metadata
    """

    def __init__(self, ipfs_client: IPFSClient, xrpl_client: XRPLClient):
        """
        Initialize anchor service.

        Args:
            ipfs_client: IPFS client instance
            xrpl_client: XRPL client instance
        """
        self.ipfs = ipfs_client
        self.xrpl = xrpl_client

    def anchor_trace(self, trace: TraceJSON) -> Dict[str, Any]:
        """
        Complete anchoring flow: IPFS upload + XRPL memo.

        Args:
            trace: TraceJSON object to anchor

        Returns:
            Dictionary with anchoring result:
            {
                "session_id": str,
                "cid": str,
                "ipfs_url": str,
                "tx_hash": str,
                "ledger_index": int,
                "merkle_root": str,
                "timestamp": int,
                "network": str
            }

        Raises:
            Exception: If IPFS upload or XRPL anchoring fails
        """
        # Step 1: Upload to IPFS
        # Use the cached JSON that was used for Merkle Root calculation
        # This ensures the Merkle Root can be verified correctly
        trace_json_str = trace.get_merkle_json()
        cid = self.ipfs.add_json_str(trace_json_str)

        # Pin the content
        self.ipfs.pin(cid)

        # Step 2: Anchor to XRPL
        xrpl_result = self.xrpl.anchor_memo(
            cid=cid,
            merkle_root=trace.hashing.chunkMerkleRoot,
            session_id=trace.session.id,
            model=trace.model.name,
            timestamp=int(datetime.now().timestamp())
        )

        # Step 3: Return complete result
        return {
            "session_id": trace.session.id,
            "cid": cid,
            "ipfs_url": f"ipfs://{cid}",
            "tx_hash": xrpl_result["tx_hash"],
            "ledger_index": xrpl_result["ledger_index"],
            "merkle_root": trace.hashing.chunkMerkleRoot,
            "timestamp": xrpl_result["memo_data"]["ts"],
            "network": xrpl_result["network"],
            "model": trace.model.name,
            "events_count": len(trace.events)
        }

    def anchor_trace_from_dict(self, trace_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anchor trace from dictionary (without TraceJSON validation).

        Args:
            trace_dict: Trace data as dictionary

        Returns:
            Anchoring result dictionary

        Raises:
            Exception: If required fields are missing or anchoring fails
        """
        # Validate required fields
        required_fields = ["session", "hashing", "model"]
        for field in required_fields:
            if field not in trace_dict:
                raise ValueError(f"Missing required field: {field}")

        session_id = trace_dict["session"]["id"]
        merkle_root = trace_dict["hashing"]["chunkMerkleRoot"]
        model_name = trace_dict["model"]["name"]

        # Step 1: Upload to IPFS
        cid = self.ipfs.add_json(trace_dict)
        self.ipfs.pin(cid)

        # Step 2: Anchor to XRPL
        xrpl_result = self.xrpl.anchor_memo(
            cid=cid,
            merkle_root=merkle_root,
            session_id=session_id,
            model=model_name,
            timestamp=int(datetime.now().timestamp())
        )

        # Step 3: Return result
        return {
            "session_id": session_id,
            "cid": cid,
            "ipfs_url": f"ipfs://{cid}",
            "tx_hash": xrpl_result["tx_hash"],
            "ledger_index": xrpl_result["ledger_index"],
            "merkle_root": merkle_root,
            "timestamp": xrpl_result["memo_data"]["ts"],
            "network": xrpl_result["network"],
            "model": model_name
        }

    def get_anchoring_status(self, tx_hash: str) -> Dict[str, Any]:
        """
        Get status of anchoring by transaction hash.

        Args:
            tx_hash: XRPL transaction hash

        Returns:
            Status dictionary with transaction and memo data

        Raises:
            Exception: If transaction retrieval fails
        """
        tx_data = self.xrpl.get_transaction(tx_hash)
        memo_data = self.xrpl.get_memo_from_transaction(tx_hash)

        return {
            "tx_hash": tx_hash,
            "status": "success" if tx_data.get("validated") else "pending",
            "ledger_index": tx_data.get("ledger_index"),
            "memo_data": memo_data,
            "timestamp": tx_data.get("date")
        }

    def close(self) -> None:
        """Close both IPFS and XRPL client connections."""
        self.ipfs.close()
        self.xrpl.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def create_anchor_service(
    ipfs_api_url: str,
    xrpl_node_url: str,
    xrpl_seed: str,
    xrpl_network: str = "testnet"
) -> AnchorService:
    """
    Factory function to create an anchor service.

    Args:
        ipfs_api_url: IPFS API endpoint
        xrpl_node_url: XRPL node URL
        xrpl_seed: XRPL wallet seed
        xrpl_network: XRPL network name

    Returns:
        AnchorService instance
    """
    from .ipfs_client import create_ipfs_client
    from .xrpl_client import create_xrpl_client

    ipfs_client = create_ipfs_client(ipfs_api_url)
    xrpl_client = create_xrpl_client(
        node_url=xrpl_node_url,
        seed=xrpl_seed,
        network=xrpl_network
    )

    return AnchorService(ipfs_client, xrpl_client)
