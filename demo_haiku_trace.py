"""Demo: Record haiku_agent execution as A2A trace"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

from a2a_anchor.trace_builder import TraceBuilder

load_dotenv()


def haiku_agent_with_trace():
    """Run haiku_agent and capture trace"""

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

    # Display final haiku
    print("\n=== Final Haiku ===")
    for msg in result['messages']:
        if hasattr(msg, 'content') and msg.content and not hasattr(msg, 'tool_calls'):
            if msg.__class__.__name__ == 'AIMessage' and not msg.tool_calls:
                print(msg.content)
                print()

    return trace, output_file


if __name__ == "__main__":
    trace, output_file = haiku_agent_with_trace()
