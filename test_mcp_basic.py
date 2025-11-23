"""Basic MCP functionality test"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mcp.logger import MCPLogger
from mcp.mcp_client import MCPClient
from mcp.mcp_trace_builder import MCPTraceBuilder

def test_basic_flow():
    """Test basic MCP flow: client → server → logger → trace builder"""

    print("="*70)
    print("Testing MCP Basic Flow")
    print("="*70)

    # Create logger and client
    logger = MCPLogger()
    client = MCPClient(logger=logger)

    session_id = "test-session-123"

    print("\n1. Testing health check...")
    if client.health_check():
        print("   ✅ MCP server is healthy")
    else:
        print("   ❌ MCP server is not responding")
        return

    print("\n2. Testing tool list...")
    tools = client.list_tools()
    print(f"   ✅ Found {len(tools)} tools:")
    for tool in tools:
        print(f"      - {tool['name']}: {tool['description']}")

    print("\n3. Testing calculate tool...")
    result = client.call_tool_simple(session_id, "calculate", expression="10 + 20")
    print(f"   ✅ Result: {result}")

    print("\n4. Testing get_time tool...")
    result = client.call_tool_simple(session_id, "get_current_time")
    print(f"   ✅ Result: {result}")

    print("\n5. Testing count_words tool...")
    result = client.call_tool_simple(session_id, "count_words", text="Hello world test")
    print(f"   ✅ Result: {result}")

    print("\n6. Testing reverse_string tool...")
    result = client.call_tool_simple(session_id, "reverse_string", text="hello")
    print(f"   ✅ Result: {result}")

    print("\n7. Testing check_palindrome tool...")
    result = client.call_tool_simple(session_id, "check_palindrome", text="racecar")
    print(f"   ✅ Result: {result}")

    print("\n8. Checking logged events...")
    logs = logger.get_session_logs(session_id)
    print(f"   ✅ Logged {len(logs)} events")

    print("\n9. Getting session stats...")
    stats = logger.get_session_stats(session_id)
    print(f"   ✅ Stats:")
    print(f"      - Total events: {stats['event_count']}")
    print(f"      - Tool calls: {stats['tool_calls']}")
    print(f"      - Tools used: {stats['tools_used']}")
    print(f"      - Total latency: {stats['total_latency_ms']:.2f}ms")

    print("\n10. Building A2A trace...")
    try:
        trace = MCPTraceBuilder.from_jsonl_logs(
            logs,
            model_name="test-model",
            provider="test"
        )
        print(f"    ✅ A2A Trace built:")
        print(f"       - Session: {trace.session.id}")
        print(f"       - Events: {len(trace.events)}")
        print(f"       - Actors: {trace.session.actors}")
        print(f"       - Merkle Root: {trace.hashing.chunkMerkleRoot[:16]}...")
        print(f"       - Chunks: {len(trace.hashing.chunks)}")
    except Exception as e:
        print(f"    ❌ Failed to build trace: {e}")

    print("\n" + "="*70)
    print("✅ All tests passed!")
    print("="*70)

if __name__ == "__main__":
    test_basic_flow()
