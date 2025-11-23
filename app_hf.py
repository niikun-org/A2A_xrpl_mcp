"""
Hugging Face Space Entry Point

This is the main entry point for HuggingFace Spaces deployment.
It starts both the MCP server and Gradio UI.
"""

import os
import subprocess
import time
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def start_mcp_server():
    """Start MCP server in background."""
    print("Starting MCP server...")

    # Start server as subprocess
    process = subprocess.Popen(
        [sys.executable, "-m", "mcp.mcp_server"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for server to be ready
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=1)
            if response.status_code == 200:
                print("✅ MCP server is ready!")
                return process
        except:
            time.sleep(1)

    print("⚠️  MCP server may not be ready")
    return process


def main():
    """Main entry point for HuggingFace Space."""
    print("="*70)
    print("MCP-Aware A2A Trace Logger - HuggingFace Space")
    print("="*70)

    # Start MCP server
    mcp_process = start_mcp_server()

    # Import and launch Gradio app
    from mcp.app import create_gradio_app

    print("\n" + "="*70)
    print("Launching Gradio UI...")
    print("="*70 + "\n")

    demo = create_gradio_app()

    try:
        # Launch with HuggingFace Space settings
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False
        )
    finally:
        # Cleanup
        if mcp_process:
            mcp_process.terminate()


if __name__ == "__main__":
    main()
