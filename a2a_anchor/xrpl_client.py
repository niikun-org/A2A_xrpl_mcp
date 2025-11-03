"""
XRPL Client for A2A Trace Anchoring

This module provides functionality to anchor A2A trace metadata to the XRP Ledger
using transaction Memos.
"""

import json
from typing import Optional, Dict, Any
from datetime import datetime

from xrpl.wallet import Wallet
from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import Payment, Memo
from xrpl.transaction import submit_and_wait, safe_sign_and_autofill_transaction
from xrpl.models.response import Response
from xrpl.utils import xrp_to_drops


class XRPLClient:
    """
    Client for interacting with XRP Ledger to anchor trace metadata.

    Attributes:
        client: XRPL JSON-RPC client
        wallet: XRPL wallet for signing transactions
        network: Network name (mainnet, testnet, devnet)
    """

    def __init__(
        self,
        node_url: str,
        seed: Optional[str] = None,
        wallet: Optional[Wallet] = None,
        network: str = "testnet"
    ):
        """
        Initialize XRPL client.

        Args:
            node_url: XRPL node JSON-RPC URL
            seed: Wallet seed (either seed or wallet must be provided)
            wallet: Pre-configured wallet (either seed or wallet must be provided)
            network: Network name (mainnet, testnet, devnet)

        Raises:
            ValueError: If neither seed nor wallet is provided
        """
        self.client = JsonRpcClient(node_url)
        self.network = network

        if wallet:
            self.wallet = wallet
        elif seed:
            self.wallet = Wallet.from_seed(seed)
        else:
            raise ValueError("Either seed or wallet must be provided")

    def anchor_memo(
        self,
        cid: str,
        merkle_root: str,
        session_id: str,
        model: str,
        timestamp: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Record trace metadata to XRPL Memo.

        Creates a payment transaction to self with a Memo containing:
        - Trace version
        - Session ID
        - IPFS CID
        - Merkle Root
        - Timestamp
        - Model name

        Args:
            cid: IPFS Content Identifier
            merkle_root: Merkle root hash of the trace
            session_id: Trace session ID
            model: Model name
            timestamp: Unix timestamp (defaults to current time)

        Returns:
            Dictionary with transaction result:
            {
                "tx_hash": str,
                "status": str,
                "ledger_index": int,
                "memo_data": dict
            }

        Raises:
            Exception: If transaction fails
        """
        if timestamp is None:
            timestamp = int(datetime.now().timestamp())

        # Prepare memo data
        memo_data = {
            "v": "a2a-0.1",
            "sid": session_id,
            "cid": cid,
            "root": merkle_root,
            "ts": timestamp,
            "model": model
        }

        # Convert memo data to hex
        memo_data_json = json.dumps(memo_data, ensure_ascii=False)
        memo_data_hex = memo_data_json.encode('utf-8').hex().upper()

        # Create memo
        memo = Memo(
            memo_data=memo_data_hex,
            memo_type="A2A_TRACE".encode('utf-8').hex().upper(),
            memo_format="json".encode('utf-8').hex().upper()
        )

        # Create payment transaction (to self)
        payment = Payment(
            account=self.wallet.address,
            destination=self.wallet.address,
            amount="1",  # 1 drop (0.000001 XRP)
            memos=[memo]
        )

        try:
            # Sign and submit transaction
            response = submit_and_wait(payment, self.client, self.wallet)

            # Check if transaction was successful
            if response.result.get("meta", {}).get("TransactionResult") != "tesSUCCESS":
                raise Exception(f"Transaction failed: {response.result}")

            tx_hash = response.result.get("hash")
            ledger_index = response.result.get("ledger_index")

            return {
                "tx_hash": tx_hash,
                "status": "success",
                "ledger_index": ledger_index,
                "memo_data": memo_data,
                "network": self.network
            }

        except Exception as e:
            raise Exception(f"Failed to anchor memo to XRPL: {e}")

    def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """
        Retrieve transaction by hash.

        Args:
            tx_hash: Transaction hash

        Returns:
            Transaction data

        Raises:
            Exception: If transaction retrieval fails
        """
        from xrpl.models.requests import Tx

        try:
            request = Tx(transaction=tx_hash)
            response = self.client.request(request)

            if not response.is_successful():
                raise Exception(f"Failed to get transaction: {response.result}")

            return response.result

        except Exception as e:
            raise Exception(f"Failed to get transaction {tx_hash}: {e}")

    def get_memo_from_transaction(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """
        Extract memo data from transaction.

        Args:
            tx_hash: Transaction hash

        Returns:
            Decoded memo data as dictionary, or None if no memo found

        Raises:
            Exception: If transaction retrieval fails or memo decoding fails
        """
        tx_data = self.get_transaction(tx_hash)

        # Get memos from transaction
        memos = tx_data.get("Memos", [])

        if not memos:
            return None

        # Get first memo (we only use one)
        memo = memos[0].get("Memo", {})
        memo_data_hex = memo.get("MemoData")

        if not memo_data_hex:
            return None

        try:
            # Decode hex to JSON
            memo_data_json = bytes.fromhex(memo_data_hex).decode('utf-8')
            memo_data = json.loads(memo_data_json)

            return memo_data

        except Exception as e:
            raise Exception(f"Failed to decode memo data: {e}")

    def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information for the wallet.

        Returns:
            Account info dictionary with balance, sequence, etc.
        """
        from xrpl.models.requests import AccountInfo

        try:
            request = AccountInfo(account=self.wallet.address)
            response = self.client.request(request)

            if not response.is_successful():
                raise Exception(f"Failed to get account info: {response.result}")

            return response.result.get("account_data", {})

        except Exception as e:
            raise Exception(f"Failed to get account info: {e}")

    def is_online(self) -> bool:
        """
        Check if XRPL node is online and accessible.

        Returns:
            True if node is accessible, False otherwise
        """
        from xrpl.models.requests import ServerInfo

        try:
            request = ServerInfo()
            response = self.client.request(request)
            return response.is_successful()
        except Exception:
            return False

    def get_network_info(self) -> Dict[str, Any]:
        """
        Get XRPL network information.

        Returns:
            Network info dictionary
        """
        from xrpl.models.requests import ServerInfo

        try:
            request = ServerInfo()
            response = self.client.request(request)

            if not response.is_successful():
                raise Exception(f"Failed to get network info: {response.result}")

            return response.result.get("info", {})

        except Exception as e:
            raise Exception(f"Failed to get network info: {e}")

    def close(self) -> None:
        """Close the XRPL client connection."""
        if hasattr(self, 'client') and self.client:
            self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def create_xrpl_client(
    node_url: str,
    seed: Optional[str] = None,
    wallet: Optional[Wallet] = None,
    network: str = "testnet"
) -> XRPLClient:
    """
    Factory function to create an XRPL client.

    Args:
        node_url: XRPL node JSON-RPC URL
        seed: Wallet seed
        wallet: Pre-configured wallet
        network: Network name

    Returns:
        XRPLClient instance
    """
    return XRPLClient(node_url=node_url, seed=seed, wallet=wallet, network=network)
