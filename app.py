#!/usr/bin/env python3
"""
HuggingFace Spaces Entry Point for A2A MCP Demo

This file is the entry point for HuggingFace Spaces deployment.
It starts both the MCP server and Gradio UI.
"""

import os
import sys
import time
import subprocess
import signal
import atexit
from pathlib import Path

# Ensure logs and traces directories exist
Path("logs").mkdir(exist_ok=True)
Path("traces").mkdir(exist_ok=True)

print("=" * 70)
print("🚀 A2A MCP Trace Logger - HuggingFace Spaces")
print("=" * 70)

# Start MCP server in background
print("\n📡 Starting MCP server...")
mcp_server_process = subprocess.Popen(
    [sys.executable, "-m", "mcp.mcp_server"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Register cleanup
def cleanup():
    """Kill MCP server on exit"""
    if mcp_server_process.poll() is None:
        print("\n🛑 Shutting down MCP server...")
        mcp_server_process.send_signal(signal.SIGTERM)
        mcp_server_process.wait(timeout=5)

atexit.register(cleanup)

# Wait for server to start
print("⏳ Waiting for MCP server to start...")
time.sleep(3)

# Check if server is running
import requests
try:
    response = requests.get("http://localhost:8000/health", timeout=5)
    if response.status_code == 200:
        print("✅ MCP server is running")
    else:
        print("⚠️  MCP server returned unexpected status")
except Exception as e:
    print(f"⚠️  Could not verify MCP server health: {e}")
    print("   Continuing anyway...")

# Import and launch Gradio app
print("\n🌐 Starting Gradio UI...")
print("=" * 70)

from mcp.app import demo

if __name__ == "__main__":
    # Launch with public sharing disabled for Spaces
    # HuggingFace Spaces will handle the hosting
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
