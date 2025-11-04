"""Demo: Full A2A Trace Anchoring - IPFS + XRPL (Phase 3)

This demo implements the complete anchoring flow:
1. Run haiku_agent
2. Build A2A trace
3. Save to local file
4. Upload to IPFS
5. Anchor to XRPL Testnet
6. Verify the complete chain

Requirements:
- IPFS node running: docker run -d --name ipfs -p 5001:5001 -p 8080:8080 ipfs/kubo
- XRPL Testnet account with XRP (get from https://xrpl.org/xrp-testnet-faucet.html)
- Environment variables: XRPL_SEED, XRPL_NODE_URL (optional)
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_core.tools import tool

from a2a_anchor.trace_builder import TraceBuilder
from a2a_anchor.ipfs_client import create_ipfs_client
from a2a_anchor.xrpl_client import create_xrpl_client
from a2a_anchor.anchor_service import AnchorService
from a2a_anchor.verify import TraceVerifier

load_dotenv()


def full_anchor_demo():
    """Run complete A2A anchoring demo with IPFS + XRPL."""

    @tool
    def check_haiku_lines(text: str) -> str:
        """Check if the given haiku text has exactly 3 lines.

        Args:
            text: The haiku text to check

        Returns:
            "OK" if the haiku has exactly 3 lines, otherwise an error message.
        """
        lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
        print(f"✓ Checking haiku ({len(lines)} lines):\n{text}\n")
        if len(lines) == 3:
            return "OK"
        else:
            return f"Error: expected 3 lines, but got {len(lines)}. Please write exactly 3 lines."

    # Create agent
    agent = create_agent(
        model="openai:gpt-5-nano",
        tools=[check_haiku_lines],
        system_prompt="""You are a sports poet who writes Haiku (3 lines).

Process:
1. Write a haiku and check it with check_haiku_lines tool
2. If tool returns "OK", refine or create another variation (repeat 2-3 times)
3. After creating 3 haikus, choose the best one and present it
4. Stop after presenting the final haiku"""
    )

    # Run agent with recursion limit
    print("="*70)
    print("PHASE 3: Full A2A Trace Anchoring - IPFS + XRPL")
    print("="*70)
    print("\n=== Step 1: Running haiku_agent ===\n")
    result = agent.invoke(
        {"messages": "please write a poem."},
        config={"recursion_limit": 25}
    )

    print("\n=== Step 2: Building A2A Trace ===")
    trace = TraceBuilder.from_langchain_result(result)

    # Display trace info
    print(f"Session ID: {trace.session.id}")
    print(f"Model: {trace.model.name}")
    print(f"Events: {len(trace.events)}")
    print(f"Actors: {', '.join(trace.session.actors)}")

    if trace.usage:
        total_input = sum(u.input_tokens for u in trace.usage)
        total_output = sum(u.output_tokens for u in trace.usage)
        print(f"Total tokens: {total_input + total_output} (input: {total_input}, output: {total_output})")

    print(f"Merkle Root: {trace.hashing.chunkMerkleRoot}")
    print(f"Chunks: {len(trace.hashing.chunks)}")

    # Save to file
    output_dir = Path("traces")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"{trace.session.id}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(trace.to_json())

    print(f"\n✓ Trace saved to: {output_file}")

    # Check IPFS
    print("\n=== Step 3: Checking IPFS Connection ===")
    try:
        ipfs_api = os.getenv("IPFS_API", "/ip4/127.0.0.1/tcp/5001/http")
        ipfs_client = create_ipfs_client(ipfs_api)

        if not ipfs_client.is_online():
            print("✗ ERROR: IPFS node is not online!")
            print("Please start IPFS node with:")
            print("  docker run -d --name ipfs -p 5001:5001 -p 8080:8080 ipfs/kubo")
            return

        version = ipfs_client.get_version()
        print(f"✓ Connected to IPFS node (version: {version.get('Version', 'unknown')})")

    except Exception as e:
        print(f"✗ ERROR: Could not connect to IPFS: {e}")
        print("Please start IPFS node with:")
        print("  docker run -d --name ipfs -p 5001:5001 -p 8080:8080 ipfs/kubo")
        return

    # Check XRPL
    print("\n=== Step 4: Checking XRPL Connection ===")
    xrpl_seed = os.getenv("XRPL_SEED")
    xrpl_node = os.getenv("XRPL_NODE_URL", "https://s.altnet.rippletest.net:51234")

    if not xrpl_seed:
        print("✗ ERROR: XRPL_SEED not configured in .env file!")
        print("\nTo get a testnet account:")
        print("1. Visit https://xrpl.org/xrp-testnet-faucet.html")
        print("2. Click 'Generate' to create a testnet account")
        print("3. Add the seed to your .env file:")
        print("   XRPL_SEED=sXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        return

    try:
        xrpl_client = create_xrpl_client(xrpl_node, seed=xrpl_seed, network="testnet")

        if not xrpl_client.is_online():
            print(f"✗ ERROR: XRPL node is not online: {xrpl_node}")
            return

        network_info = xrpl_client.get_network_info()
        print(f"✓ Connected to XRPL Testnet")
        print(f"  Node: {xrpl_node}")
        print(f"  Network: testnet")

        # Get account info
        account_info = xrpl_client.get_account_info()
        balance_xrp = int(account_info["Balance"]) / 1_000_000
        print(f"  Account: {xrpl_client.wallet.address}")
        print(f"  Balance: {balance_xrp:.6f} XRP")

        if balance_xrp < 10:
            print(f"\n⚠ WARNING: Low balance ({balance_xrp:.6f} XRP)")
            print("  Get more testnet XRP from: https://xrpl.org/xrp-testnet-faucet.html")

    except Exception as e:
        print(f"✗ ERROR: Could not connect to XRPL: {e}")
        return

    # Create anchor service
    print("\n=== Step 5: Anchoring to IPFS + XRPL ===")
    try:
        anchor_service = AnchorService(ipfs_client, xrpl_client)

        print("Uploading to IPFS...")
        print("Anchoring to XRPL Testnet...")
        print("(This may take 4-5 seconds for ledger validation...)")

        anchor_result = anchor_service.anchor_trace(trace)

        print(f"\n✓ Anchoring Complete!")
        print(f"  Session ID: {anchor_result['session_id']}")
        print(f"  IPFS CID: {anchor_result['cid']}")
        print(f"  IPFS URL: {anchor_result['ipfs_url']}")
        print(f"  Gateway URL: http://localhost:8080/ipfs/{anchor_result['cid']}")
        print(f"  XRPL TX Hash: {anchor_result['tx_hash']}")
        print(f"  Ledger Index: {anchor_result['ledger_index']}")
        print(f"  Merkle Root: {anchor_result['merkle_root']}")
        print(f"  Timestamp: {anchor_result['timestamp']}")

        # Verify
        print("\n=== Step 6: Verifying Anchored Trace ===")
        verifier = TraceVerifier(xrpl_client, ipfs_client)

        print(f"Verifying transaction: {anchor_result['tx_hash']}")
        print("1. Retrieving memo from XRPL...")
        print("2. Fetching trace from IPFS...")
        print("3. Recalculating Merkle Root...")
        print("4. Comparing with anchored root...")

        verification = verifier.verify(anchor_result['tx_hash'])

        print(f"\n{'='*70}")
        if verification.verified:
            print("✓ VERIFICATION PASSED")
            print(f"{'='*70}")
            print(f"  Session ID: {verification.session_id}")
            print(f"  IPFS CID: {verification.cid}")
            print(f"  Expected Root: {verification.expected_root}")
            print(f"  Computed Root: {verification.computed_root}")
            print(f"  Match: {'✓ YES' if verification.expected_root == verification.computed_root else '✗ NO'}")
            print(f"  Model: {verification.details.get('model')}")
            print(f"  Events: {verification.details.get('trace_events')}")
            print(f"  Chunks: {verification.details.get('chunks')}")
        else:
            print("✗ VERIFICATION FAILED")
            print(f"{'='*70}")
            print(f"  Error: {verification.error}")

        # Cleanup
        anchor_service.close()

        # Display final haiku
        print("\n=== Final Haiku ===")
        for msg in result['messages']:
            if hasattr(msg, 'content') and msg.content and not hasattr(msg, 'tool_calls'):
                if msg.__class__.__name__ == 'AIMessage' and not msg.tool_calls:
                    print(msg.content)
                    print()

        # Summary
        print(f"\n{'='*70}")
        print("SUCCESS: Complete A2A Trace Anchoring")
        print(f"{'='*70}")
        print(f"\nLocal File: {output_file}")
        print(f"IPFS CID: {anchor_result['cid']}")
        print(f"XRPL TX: {anchor_result['tx_hash']}")
        print(f"\nExplore on XRPL:")
        print(f"  https://testnet.xrpl.org/transactions/{anchor_result['tx_hash']}")
        print(f"\nVerify anytime with:")
        print(f"  uv run python -c \"")
        print(f"from a2a_anchor.xrpl_client import create_xrpl_client;")
        print(f"from a2a_anchor.ipfs_client import create_ipfs_client;")
        print(f"from a2a_anchor.verify import verify_trace;")
        print(f"xrpl = create_xrpl_client('{xrpl_node}', seed='{xrpl_seed[:10]}...', network='testnet');")
        print(f"ipfs = create_ipfs_client();")
        print(f"result = verify_trace('{anchor_result['tx_hash']}', xrpl, ipfs);")
        print(f"print(result)\"")

        return anchor_result

    except Exception as e:
        print(f"\n✗ ERROR during anchoring: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = full_anchor_demo()

    if not result:
        print("\n" + "="*70)
        print("Anchoring failed - please check the errors above")
        print("="*70)
