"""Merkle Tree computation for trace chunks"""

import hashlib
from typing import List, Tuple


def sha256_hash(data: str) -> str:
    """Compute SHA256 hash of string data"""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def chunk_data(data: str, chunk_size: int = 4096) -> List[str]:
    """Split data into fixed-size chunks"""
    chunks = []
    for i in range(0, len(data), chunk_size):
        chunks.append(data[i:i + chunk_size])
    return chunks


def compute_merkle_root(chunks: List[str]) -> Tuple[str, List[str]]:
    """
    Compute Merkle root from data chunks

    Args:
        chunks: List of data chunks

    Returns:
        Tuple of (merkle_root, chunk_hashes)
    """
    if not chunks:
        return sha256_hash(""), []

    # Hash each chunk
    chunk_hashes = [sha256_hash(chunk) for chunk in chunks]

    # If only one chunk, return its hash as root
    if len(chunk_hashes) == 1:
        return chunk_hashes[0], chunk_hashes

    # Build Merkle tree
    current_level = chunk_hashes[:]

    while len(current_level) > 1:
        next_level = []

        # Process pairs
        for i in range(0, len(current_level), 2):
            if i + 1 < len(current_level):
                # Hash pair
                combined = current_level[i] + current_level[i + 1]
                next_level.append(sha256_hash(combined))
            else:
                # Odd number of nodes - promote last node
                next_level.append(current_level[i])

        current_level = next_level

    return current_level[0], chunk_hashes


def compute_trace_merkle(trace_json: str, chunk_size: int = 4096) -> Tuple[str, List[str]]:
    """
    Compute Merkle root for a trace JSON string

    Args:
        trace_json: JSON string of the trace
        chunk_size: Size of each chunk in bytes

    Returns:
        Tuple of (merkle_root, chunk_hashes)
    """
    chunks = chunk_data(trace_json, chunk_size)
    return compute_merkle_root(chunks)
