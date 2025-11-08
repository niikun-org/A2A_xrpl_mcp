"""
IPFS Client for A2A Trace Anchoring

This module provides a simple interface to interact with IPFS (InterPlanetary File System)
for storing and retrieving A2A trace JSON files.
"""

import json
from typing import Optional
import ipfshttpclient


class IPFSClient:
    """
    Client for interacting with IPFS node via HTTP API.

    Attributes:
        client: IPFS HTTP client instance
        api_url: IPFS API endpoint URL
    """

    def __init__(self, api_url: str = '/ip4/127.0.0.1/tcp/5001/http'):
        """
        Initialize IPFS client.

        Args:
            api_url: IPFS API multiaddr (default: local node at port 5001)

        Raises:
            ipfshttpclient.exceptions.ConnectionError: If connection to IPFS node fails
        """
        self.api_url = api_url
        try:
            self.client = ipfshttpclient.connect(api_url)
        except Exception as e:
            raise ConnectionError(f"Failed to connect to IPFS node at {api_url}: {e}")

    def add_json(self, trace_json: dict) -> str:
        """
        Upload trace JSON to IPFS and return CID.

        Args:
            trace_json: Trace data as dictionary

        Returns:
            CID (Content Identifier) as string (e.g., 'bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi')

        Raises:
            ValueError: If trace_json is invalid
            Exception: If IPFS upload fails
        """
        if not isinstance(trace_json, dict):
            raise ValueError("trace_json must be a dictionary")

        try:
            # Convert to JSON string with consistent formatting
            # This is important for Merkle Root verification
            json_str = json.dumps(trace_json, ensure_ascii=False, indent=2)

            # Add JSON string to IPFS as a file (not using add_json which doesn't preserve formatting)
            result = self.client.add_str(json_str)

            return result
        except Exception as e:
            raise Exception(f"Failed to add JSON to IPFS: {e}")

    def add_json_str(self, json_str: str) -> str:
        """
        Upload trace JSON string to IPFS and return CID.

        This preserves the exact JSON formatting, which is important for Merkle Root verification.

        Args:
            json_str: Trace data as JSON string

        Returns:
            CID (Content Identifier) as string

        Raises:
            ValueError: If json_str is not valid JSON
            Exception: If IPFS upload fails
        """
        try:
            # Validate JSON
            json.loads(json_str)

            # Upload string directly to preserve formatting
            result = self.client.add_str(json_str)
            return result
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {e}")
        except Exception as e:
            raise Exception(f"Failed to add JSON string to IPFS: {e}")

    def get_json(self, cid: str) -> dict:
        """
        Retrieve JSON from IPFS by CID.

        Args:
            cid: Content Identifier

        Returns:
            Trace data as dictionary

        Raises:
            ValueError: If CID is invalid
            Exception: If IPFS retrieval fails
        """
        if not cid or not isinstance(cid, str):
            raise ValueError("CID must be a non-empty string")

        try:
            # Get content as string (to preserve formatting for Merkle Root verification)
            json_str = self.client.cat(cid).decode('utf-8')
            result = json.loads(json_str)
            return result
        except Exception as e:
            raise Exception(f"Failed to get JSON from IPFS (CID: {cid}): {e}")

    def get_json_str(self, cid: str) -> str:
        """
        Retrieve JSON string from IPFS by CID.

        This preserves the exact formatting, which is important for Merkle Root verification.

        Args:
            cid: Content Identifier

        Returns:
            Trace data as JSON string

        Raises:
            ValueError: If CID is invalid
            Exception: If IPFS retrieval fails
        """
        if not cid or not isinstance(cid, str):
            raise ValueError("CID must be a non-empty string")

        try:
            json_str = self.client.cat(cid).decode('utf-8')
            return json_str
        except Exception as e:
            raise Exception(f"Failed to get JSON string from IPFS (CID: {cid}): {e}")

    def pin(self, cid: str) -> None:
        """
        Pin content to ensure it's not garbage collected.

        Args:
            cid: Content Identifier to pin

        Raises:
            Exception: If pinning fails
        """
        try:
            self.client.pin.add(cid)
        except Exception as e:
            raise Exception(f"Failed to pin CID {cid}: {e}")

    def unpin(self, cid: str) -> None:
        """
        Unpin content to allow garbage collection.

        Args:
            cid: Content Identifier to unpin

        Raises:
            Exception: If unpinning fails
        """
        try:
            self.client.pin.rm(cid)
        except Exception as e:
            raise Exception(f"Failed to unpin CID {cid}: {e}")

    def is_online(self) -> bool:
        """
        Check if IPFS node is online and accessible.

        Returns:
            True if node is accessible, False otherwise
        """
        try:
            self.client.version()
            return True
        except Exception:
            return False

    def get_version(self) -> dict:
        """
        Get IPFS node version information.

        Returns:
            Dictionary with version info
        """
        try:
            return self.client.version()
        except Exception as e:
            raise Exception(f"Failed to get IPFS version: {e}")

    def close(self) -> None:
        """Close the IPFS client connection."""
        if hasattr(self, 'client') and self.client:
            self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def create_ipfs_client(api_url: Optional[str] = None) -> IPFSClient:
    """
    Factory function to create an IPFS client.

    Args:
        api_url: IPFS API endpoint (default: local node)

    Returns:
        IPFSClient instance
    """
    if api_url is None:
        api_url = '/ip4/127.0.0.1/tcp/5001/http'

    return IPFSClient(api_url)
