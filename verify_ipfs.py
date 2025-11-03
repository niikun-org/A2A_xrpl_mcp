#!/usr/bin/env python3
"""
IPFS Verification Script

Simple script to verify IPFS content by CID
"""

import sys
import json
from a2a_anchor.ipfs_client import create_ipfs_client

def verify_cid(cid: str):
    """Verify and display content from IPFS by CID"""

    print(f"🔍 Verifying CID: {cid}\n")

    try:
        # Create IPFS client
        client = create_ipfs_client()

        # Check connection
        if not client.is_online():
            print("❌ ERROR: IPFS node is not online")
            print("\nPlease start IPFS with:")
            print("  docker run -d --name ipfs -p 5001:5001 -p 8080:8080 ipfs/kubo")
            return False

        print("✓ Connected to IPFS node")

        # Fetch content
        print(f"\n📥 Fetching content from CID...")
        content = client.get_json(cid)

        print("✓ Content retrieved successfully!\n")

        # Display summary
        print("="*70)
        print("CONTENT SUMMARY")
        print("="*70)

        if isinstance(content, dict):
            # A2A Trace format
            if "traceVersion" in content:
                print(f"\n📋 A2A Trace (version: {content.get('traceVersion')})")
                print(f"   Session ID: {content.get('session', {}).get('id')}")
                print(f"   Model: {content.get('model', {}).get('name')}")
                print(f"   Events: {len(content.get('events', []))}")
                print(f"   Merkle Root: {content.get('hashing', {}).get('chunkMerkleRoot', 'N/A')[:50]}...")
            else:
                # Generic JSON
                print("\n📄 JSON Object")
                print(f"   Keys: {', '.join(content.keys())}")

        # Display full JSON
        print(f"\n{'='*70}")
        print("FULL CONTENT (formatted JSON)")
        print(f"{'='*70}\n")
        print(json.dumps(content, indent=2, ensure_ascii=False))

        # Gateway URLs
        print(f"\n{'='*70}")
        print("ACCESS URLS")
        print(f"{'='*70}")
        print(f"\n🌐 IPFS Gateway:")
        print(f"   http://127.0.0.1:8080/ipfs/{cid}")
        print(f"\n🔗 IPFS Protocol:")
        print(f"   ipfs://{cid}")

        client.close()
        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_ipfs.py <CID>")
        print("\nExample:")
        print("  python verify_ipfs.py QmNnr7tpaejPtQmwHXC4ffEYTPiwvncnetAFfRds8Upsti")
        sys.exit(1)

    cid = sys.argv[1]
    success = verify_cid(cid)
    sys.exit(0 if success else 1)
