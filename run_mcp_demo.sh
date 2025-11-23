#!/bin/bash

# MCP-Aware A2A Trace Logger - Startup Script

echo "======================================================================"
echo "MCP-Aware A2A Trace Logger"
echo "======================================================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  WARNING: .env file not found!"
    echo "   Please create .env with XRPL_SEED"
    echo "   Get testnet account: https://xrpl.org/xrp-testnet-faucet.html"
    echo ""
fi

# Check if IPFS is running
echo "Checking IPFS..."
if ! curl -s http://127.0.0.1:5001/api/v0/version > /dev/null 2>&1; then
    echo "⚠️  IPFS is not running!"
    echo "   Start with: docker run -d --name ipfs -p 5001:5001 -p 8080:8080 ipfs/kubo"
    echo ""
else
    echo "✅ IPFS is running"
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements-mcp.txt

echo ""
echo "======================================================================"
echo "Starting MCP Server and Gradio UI"
echo "======================================================================"
echo ""

# Start MCP server in background
echo "Starting MCP server on port 8000..."
python -m mcp.mcp_server &
MCP_SERVER_PID=$!

# Wait for server to start
sleep 2

# Check if MCP server is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Failed to start MCP server!"
    exit 1
fi

echo "✅ MCP server started (PID: $MCP_SERVER_PID)"
echo ""

# Start Gradio UI
echo "Starting Gradio UI on port 7860..."
echo ""
echo "======================================================================"
echo "🚀 Access the UI at: http://localhost:7860"
echo "======================================================================"
echo ""

python -m mcp.app

# Cleanup on exit
trap "kill $MCP_SERVER_PID 2>/dev/null" EXIT
