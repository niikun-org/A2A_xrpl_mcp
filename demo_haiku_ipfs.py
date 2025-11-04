"""Demo: Record haiku_agent execution as A2A trace and store in IPFS

This demo extends demo_haiku_trace.py to include Phase 2 functionality:
- Saves trace JSON to local file
- Uploads trace to IPFS
- Returns CID for verification

Requirements:
- IPFS node running at localhost:5001
  Run: docker run -d --name ipfs -p 5001:5001 -p 8080:8080 ipfs/kubo
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

from a2a_anchor.trace_builder import TraceBuilder
from a2a_anchor.ipfs_client import create_ipfs_client

load_dotenv()


def haiku_agent_with_ipfs():
    """Run haiku_agent, capture trace, and store in IPFS"""

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
    print("=== Running haiku_agent ===\n")
    result = agent.invoke(
        {"messages": "please write a poem."},
        config={"recursion_limit": 25}
    )

    print("\n=== Agent Result ===")
    print(f"Messages: {len(result['messages'])} messages")

    # Build trace
    print("\n=== Building A2A Trace ===")
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

    print(f"\n=== Trace saved to: {output_file} ===")

    # Phase 2: Upload to IPFS
    print("\n=== Phase 2: Uploading to IPFS ===")
    try:
        # Create IPFS client
        ipfs_client = create_ipfs_client()

        # Check IPFS connection
        if not ipfs_client.is_online():
            print("ERROR: IPFS node is not online!")
            print("Please start IPFS node with:")
            print("  docker run -d --name ipfs -p 5001:5001 -p 8080:8080 ipfs/kubo")
            return trace, output_file, None

        # Get IPFS version
        version = ipfs_client.get_version()
        print(f"Connected to IPFS node (version: {version.get('Version', 'unknown')})")

        # Upload trace to IPFS
        trace_dict = json.loads(trace.to_json())
        cid = ipfs_client.add_json(trace_dict)

        print(f"✓ Trace uploaded to IPFS")
        print(f"  CID: {cid}")
        print(f"  IPFS URL: ipfs://{cid}")
        print(f"  Gateway URL: http://localhost:8080/ipfs/{cid}")

        # Pin the content
        ipfs_client.pin(cid)
        print(f"✓ Content pinned to prevent garbage collection")

        # Verify retrieval
        print("\n=== Verifying IPFS retrieval ===")
        retrieved = ipfs_client.get_json(cid)

        # Verify merkle root matches
        if retrieved.get("hashing", {}).get("chunkMerkleRoot") == trace.hashing.chunkMerkleRoot:
            print("✓ Merkle Root verification: PASSED")
            print(f"  Expected: {trace.hashing.chunkMerkleRoot}")
            print(f"  Retrieved: {retrieved['hashing']['chunkMerkleRoot']}")
        else:
            print("✗ Merkle Root verification: FAILED")
            return trace, output_file, None

        ipfs_client.close()

        print("\n=== Phase 2 Complete ===")
        print(f"Local file: {output_file}")
        print(f"IPFS CID: {cid}")

        return trace, output_file, cid

    except ConnectionError as e:
        print(f"\nERROR: Could not connect to IPFS node: {e}")
        print("Please start IPFS node with:")
        print("  docker run -d --name ipfs -p 5001:5001 -p 8080:8080 ipfs/kubo")
        return trace, output_file, None
    except Exception as e:
        print(f"\nERROR during IPFS upload: {e}")
        return trace, output_file, None

    finally:
        # Display final haiku
        print("\n=== Final Haiku ===")
        for msg in result['messages']:
            if hasattr(msg, 'content') and msg.content and not hasattr(msg, 'tool_calls'):
                if msg.__class__.__name__ == 'AIMessage' and not msg.tool_calls:
                    print(msg.content)
                    print()


if __name__ == "__main__":
    trace, output_file, cid = haiku_agent_with_ipfs()

    if cid:
        print(f"\n{'='*60}")
        print("SUCCESS: Trace recorded and anchored to IPFS!")
        print(f"{'='*60}")
        print(f"Session ID: {trace.session.id}")
        print(f"Local file: {output_file}")
        print(f"IPFS CID: {cid}")
        print(f"Merkle Root: {trace.hashing.chunkMerkleRoot}")
        print(f"\nNext steps:")
        print(f"- Verify trace: uv run python -c \"from a2a_anchor.ipfs_client import create_ipfs_client; print(create_ipfs_client().get_json('{cid}')['session']['id'])\"")
        print(f"- View in browser: http://localhost:8080/ipfs/{cid}")
    else:
        print(f"\nTrace saved locally to: {output_file}")
        print("IPFS upload skipped (node not available)")
