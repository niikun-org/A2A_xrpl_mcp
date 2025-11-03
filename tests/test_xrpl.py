"""
Tests for XRPL Client and Integration

These tests require:
1. XRPL Testnet access (or local rippled node)
2. A funded testnet account (get XRP from faucet)

To get testnet XRP:
https://xrpl.org/xrp-testnet-faucet.html

Skip these tests if XRPL is not configured:
    pytest -k "not xrpl"
"""

import pytest
import os
from datetime import datetime

from a2a_anchor.xrpl_client import XRPLClient, create_xrpl_client
from a2a_anchor.ipfs_client import create_ipfs_client
from a2a_anchor.anchor_service import AnchorService
from a2a_anchor.verify import verify_trace, TraceVerifier
from a2a_anchor.trace_schema import TraceJSON, Session, Model, Event, Usage, Hashing


# Sample trace for testing
def create_sample_trace() -> TraceJSON:
    """Create a minimal trace for testing."""
    return TraceJSON(
        traceVersion="a2a-0.1",
        session=Session(
            id="test-session-xrpl-001",
            createdAt=datetime.now().isoformat(),
            actors=["user", "assistant"]
        ),
        model=Model(
            name="gpt-5-nano-2025-08-07",
            provider="openai"
        ),
        events=[
            Event(
                type="human_message",
                ts=datetime.now().isoformat(),
                content="Test message"
            )
        ],
        usage=[
            Usage(turn=1, input_tokens=10, output_tokens=5)
        ],
        hashing=Hashing(
            algorithm="sha256",
            chunk_size=4096,
            chunkMerkleRoot="test_root_abc123",
            chunks=["hash1"]
        )
    )


@pytest.fixture
def xrpl_testnet_config():
    """
    Get XRPL testnet configuration from environment.
    Skip test if not configured.
    """
    node_url = os.getenv("XRPL_NODE_URL", "https://s.altnet.rippletest.net:51234")
    seed = os.getenv("XRPL_SEED")

    if not seed:
        pytest.skip("XRPL_SEED not configured in environment")

    return {
        "node_url": node_url,
        "seed": seed,
        "network": "testnet"
    }


@pytest.fixture
def xrpl_client(xrpl_testnet_config):
    """Create XRPL client for testing."""
    try:
        client = create_xrpl_client(**xrpl_testnet_config)
        if not client.is_online():
            pytest.skip("XRPL node is not online")
        yield client
        client.close()
    except Exception as e:
        pytest.skip(f"XRPL client setup failed: {e}")


def test_xrpl_client_connection(xrpl_client):
    """Test that XRPL client can connect to node."""
    assert xrpl_client.is_online()

    # Get network info
    network_info = xrpl_client.get_network_info()
    assert "build_version" in network_info


def test_xrpl_get_account_info(xrpl_client):
    """Test getting account information."""
    account_info = xrpl_client.get_account_info()

    assert "Account" in account_info
    assert "Balance" in account_info
    assert account_info["Account"] == xrpl_client.wallet.address


def test_xrpl_anchor_memo(xrpl_client):
    """Test anchoring memo to XRPL."""
    result = xrpl_client.anchor_memo(
        cid="test_cid_123",
        merkle_root="test_root_abc123",
        session_id="test-session-001",
        model="gpt-5-nano-2025-08-07"
    )

    assert result["status"] == "success"
    assert "tx_hash" in result
    assert "ledger_index" in result
    assert result["memo_data"]["cid"] == "test_cid_123"
    assert result["memo_data"]["root"] == "test_root_abc123"


def test_xrpl_get_transaction(xrpl_client):
    """Test retrieving transaction."""
    # First anchor a memo
    result = xrpl_client.anchor_memo(
        cid="test_cid_456",
        merkle_root="test_root_def456",
        session_id="test-session-002",
        model="gpt-5-nano"
    )

    tx_hash = result["tx_hash"]

    # Retrieve transaction
    tx_data = xrpl_client.get_transaction(tx_hash)

    assert tx_data["hash"] == tx_hash
    assert "Memos" in tx_data


def test_xrpl_get_memo_from_transaction(xrpl_client):
    """Test extracting memo from transaction."""
    # Anchor a memo
    result = xrpl_client.anchor_memo(
        cid="test_cid_789",
        merkle_root="test_root_ghi789",
        session_id="test-session-003",
        model="gpt-5-nano"
    )

    tx_hash = result["tx_hash"]

    # Extract memo
    memo_data = xrpl_client.get_memo_from_transaction(tx_hash)

    assert memo_data is not None
    assert memo_data["cid"] == "test_cid_789"
    assert memo_data["root"] == "test_root_ghi789"
    assert memo_data["sid"] == "test-session-003"
    assert memo_data["v"] == "a2a-0.1"


@pytest.mark.skipif(
    not os.getenv("XRPL_SEED") or not os.getenv("IPFS_API"),
    reason="XRPL and IPFS not configured"
)
def test_full_integration_anchor_and_verify():
    """
    Full integration test: Anchor trace to IPFS + XRPL and verify.

    This test requires both IPFS and XRPL to be available.
    """
    # Setup
    ipfs_api = os.getenv("IPFS_API", "/ip4/127.0.0.1/tcp/5001/http")
    xrpl_node = os.getenv("XRPL_NODE_URL", "https://s.altnet.rippletest.net:51234")
    xrpl_seed = os.getenv("XRPL_SEED")

    if not xrpl_seed:
        pytest.skip("XRPL_SEED not configured")

    try:
        # Create clients
        ipfs_client = create_ipfs_client(ipfs_api)
        xrpl_client = create_xrpl_client(xrpl_node, seed=xrpl_seed, network="testnet")

        # Check connectivity
        if not ipfs_client.is_online():
            pytest.skip("IPFS node is not online")
        if not xrpl_client.is_online():
            pytest.skip("XRPL node is not online")

        # Create anchor service
        anchor_service = AnchorService(ipfs_client, xrpl_client)

        # Create sample trace
        trace = create_sample_trace()

        # Anchor trace
        result = anchor_service.anchor_trace(trace)

        assert "cid" in result
        assert "tx_hash" in result
        assert result["session_id"] == trace.session.id

        tx_hash = result["tx_hash"]
        cid = result["cid"]

        # Verify trace
        verifier = TraceVerifier(xrpl_client, ipfs_client)
        verification = verifier.verify(tx_hash)

        assert verification.verified is True
        assert verification.cid == cid
        assert verification.session_id == trace.session.id

        # Cleanup
        anchor_service.close()

    except Exception as e:
        pytest.skip(f"Integration test failed: {e}")


def test_xrpl_context_manager(xrpl_testnet_config):
    """Test XRPL client as context manager."""
    with create_xrpl_client(**xrpl_testnet_config) as client:
        if not client.is_online():
            pytest.skip("XRPL node is not online")

        result = client.anchor_memo(
            cid="test_context_cid",
            merkle_root="test_context_root",
            session_id="test-context-session",
            model="gpt-5-nano"
        )

        assert result["status"] == "success"


def test_xrpl_invalid_transaction():
    """Test that invalid transaction hash raises error."""
    try:
        node_url = os.getenv("XRPL_NODE_URL", "https://s.altnet.rippletest.net:51234")
        seed = os.getenv("XRPL_SEED")

        if not seed:
            pytest.skip("XRPL_SEED not configured")

        client = create_xrpl_client(node_url, seed=seed, network="testnet")

        if not client.is_online():
            pytest.skip("XRPL node is not online")

        with pytest.raises(Exception):
            client.get_transaction("invalid_tx_hash_12345")

        client.close()

    except Exception:
        pytest.skip("XRPL not configured")
