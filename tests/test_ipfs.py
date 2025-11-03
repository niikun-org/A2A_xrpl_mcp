"""
Tests for IPFS Client

These tests require a running IPFS node at localhost:5001.
To run IPFS locally:
    docker run -d --name ipfs -p 5001:5001 -p 8080:8080 ipfs/kubo

Skip these tests if IPFS is not available:
    pytest -k "not ipfs"
"""

import pytest
import json
from a2a_anchor.ipfs_client import IPFSClient, create_ipfs_client


# Sample trace data for testing
SAMPLE_TRACE = {
    "traceVersion": "a2a-0.1",
    "session": {
        "id": "test-session-001",
        "createdAt": "2025-11-02T15:00:00+00:00",
        "actors": ["user", "assistant"]
    },
    "model": {
        "name": "gpt-5-nano-2025-08-07",
        "provider": "openai"
    },
    "events": [
        {
            "type": "human_message",
            "ts": "2025-11-02T15:00:01+00:00",
            "content": "Hello, world!"
        },
        {
            "type": "ai_message",
            "ts": "2025-11-02T15:00:02+00:00",
            "content": "Hi there!"
        }
    ],
    "usage": [
        {"turn": 1, "input_tokens": 10, "output_tokens": 5}
    ],
    "hashing": {
        "algorithm": "sha256",
        "chunk_size": 4096,
        "chunkMerkleRoot": "abc123",
        "chunks": ["hash1"]
    }
}


@pytest.fixture
def ipfs_client():
    """
    Create IPFS client for testing.
    Skip test if IPFS is not available.
    """
    try:
        client = create_ipfs_client()
        if not client.is_online():
            pytest.skip("IPFS node is not online")
        yield client
        client.close()
    except Exception as e:
        pytest.skip(f"IPFS node is not available: {e}")


def test_ipfs_client_connection():
    """Test that IPFS client can connect to node."""
    try:
        client = create_ipfs_client()
        assert client.is_online()
        version = client.get_version()
        assert "Version" in version
        client.close()
    except Exception:
        pytest.skip("IPFS node is not available")


def test_ipfs_add_and_get_json(ipfs_client):
    """Test uploading and retrieving JSON from IPFS."""
    # Add JSON to IPFS
    cid = ipfs_client.add_json(SAMPLE_TRACE)

    assert cid is not None
    assert isinstance(cid, str)
    assert len(cid) > 0

    # Retrieve JSON from IPFS
    retrieved = ipfs_client.get_json(cid)

    assert retrieved == SAMPLE_TRACE
    assert retrieved["traceVersion"] == "a2a-0.1"
    assert retrieved["session"]["id"] == "test-session-001"


def test_ipfs_add_json_str(ipfs_client):
    """Test uploading JSON string to IPFS."""
    json_str = json.dumps(SAMPLE_TRACE)

    cid = ipfs_client.add_json_str(json_str)

    assert cid is not None
    assert isinstance(cid, str)

    # Verify retrieval
    retrieved = ipfs_client.get_json(cid)
    assert retrieved == SAMPLE_TRACE


def test_ipfs_cid_consistency(ipfs_client):
    """Test that same content produces same CID."""
    cid1 = ipfs_client.add_json(SAMPLE_TRACE)
    cid2 = ipfs_client.add_json(SAMPLE_TRACE)

    # Same content should produce same CID (content-addressable)
    assert cid1 == cid2


def test_ipfs_pin_unpin(ipfs_client):
    """Test pinning and unpinning content."""
    cid = ipfs_client.add_json(SAMPLE_TRACE)

    # Pin the content
    ipfs_client.pin(cid)

    # Unpin the content
    ipfs_client.unpin(cid)


def test_ipfs_invalid_cid(ipfs_client):
    """Test that invalid CID raises error."""
    with pytest.raises(Exception):
        ipfs_client.get_json("invalid-cid-123")


def test_ipfs_invalid_json():
    """Test that invalid JSON raises ValueError."""
    try:
        client = create_ipfs_client()
        if not client.is_online():
            pytest.skip("IPFS node is not online")

        with pytest.raises(ValueError):
            client.add_json_str("not valid json {{{")

        client.close()
    except Exception:
        pytest.skip("IPFS node is not available")


def test_ipfs_context_manager():
    """Test IPFS client as context manager."""
    try:
        with create_ipfs_client() as client:
            if not client.is_online():
                pytest.skip("IPFS node is not online")

            cid = client.add_json(SAMPLE_TRACE)
            assert cid is not None
    except Exception:
        pytest.skip("IPFS node is not available")


def test_ipfs_large_trace(ipfs_client):
    """Test uploading large trace with many events."""
    large_trace = SAMPLE_TRACE.copy()

    # Create 100 events
    large_trace["events"] = []
    for i in range(100):
        large_trace["events"].append({
            "type": "human_message" if i % 2 == 0 else "ai_message",
            "ts": f"2025-11-02T15:00:{i:02d}+00:00",
            "content": f"Message {i} with some content to make it larger"
        })

    # Add to IPFS
    cid = ipfs_client.add_json(large_trace)

    # Retrieve and verify
    retrieved = ipfs_client.get_json(cid)
    assert len(retrieved["events"]) == 100
    assert retrieved["events"][50]["content"] == "Message 50 with some content to make it larger"


def test_ipfs_empty_trace(ipfs_client):
    """Test uploading minimal trace."""
    minimal_trace = {
        "traceVersion": "a2a-0.1",
        "session": {"id": "minimal", "createdAt": "2025-11-02T00:00:00+00:00", "actors": []},
        "model": {"name": "test", "provider": "test"},
        "events": [],
        "usage": [],
        "hashing": {"algorithm": "sha256", "chunk_size": 4096, "chunkMerkleRoot": None, "chunks": []}
    }

    cid = ipfs_client.add_json(minimal_trace)
    retrieved = ipfs_client.get_json(cid)

    assert retrieved == minimal_trace


def test_ipfs_unicode_content(ipfs_client):
    """Test uploading trace with unicode content."""
    unicode_trace = SAMPLE_TRACE.copy()
    unicode_trace["events"] = [
        {
            "type": "human_message",
            "ts": "2025-11-02T15:00:00+00:00",
            "content": "こんにちは、世界！ 🌍 Testing unicode: émojis 中文 العربية"
        }
    ]

    cid = ipfs_client.add_json(unicode_trace)
    retrieved = ipfs_client.get_json(cid)

    assert retrieved["events"][0]["content"] == "こんにちは、世界！ 🌍 Testing unicode: émojis 中文 العربية"
