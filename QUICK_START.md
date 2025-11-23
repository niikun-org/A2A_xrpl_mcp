# 🚀 Quick Start Guide

## Prerequisites

### Docker Installation Required

This project requires **Docker** to run IPFS for full anchoring functionality.

**Install Docker:**
- **Mac/Windows**: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Linux**:
  ```bash
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
  ```

**Verify Docker is running:**
```bash
docker --version
docker ps
```

---

## For Local Development

### 1. Start IPFS (Required for anchoring features)

**First time setup:**
```bash
# Pull IPFS image and start container
docker run -d --name ipfs -p 5001:5001 -p 8080:8080 ipfs/kubo

# Verify IPFS is running
curl http://localhost:5001/api/v0/version
```

**If container already exists:**
```bash
# Check container status
docker ps -a | grep ipfs

# Start existing container
docker start ipfs

# If you need to recreate it
docker rm -f ipfs
docker run -d --name ipfs -p 5001:5001 -p 8080:8080 ipfs/kubo
```

### 2. Configure XRPL (Optional but recommended for anchoring)

```bash
# Get testnet account from https://xrpl.org/xrp-testnet-faucet.html
# Then create .env file:
echo "XRPL_SEED=sXXXXXXXXXXXXXXXXXXXXXXX" > .env
```

### 3. Install Dependencies

```bash
pip install -r requirements-mcp.txt
```

### 4. Run the Demo

```bash
./run_mcp_demo.sh
```

**Or run components separately:**

```bash
# Terminal 1: Start MCP Server
python -m mcp.mcp_server

# Terminal 2: Start Gradio UI
python -m mcp.app
```

### 5. Access the UI

Open your browser to: **http://localhost:7860**

---

## For HuggingFace Spaces

Simply click "Deploy" and the Space will automatically:
1. Start MCP server in background
2. Launch Gradio UI
3. Be ready to use!

**Note**: Full IPFS + XRPL anchoring requires local setup with proper credentials.

---

## Example Prompts

Try these in the chat interface:

- "Calculate 25 * 4"
- "What time is it?"
- "Count words in this sentence: hello world test"
- "Reverse 'hello world'"
- "Is 'racecar' a palindrome?"

---

## Anchoring Workflow

1. **Chat** with the AI and watch it use tools
2. **View statistics** in the right panel
3. **Click "Anchor Session Logs"** button
4. **Get results** with:
   - IPFS CID
   - XRPL Transaction Hash
   - Merkle Root
   - Explorer link

5. **Verify** on XRPL Testnet Explorer

---

## Troubleshooting

### MCP Server not responding?

```bash
# Check if server is running
curl http://localhost:8000/health

# Should return: {"status":"healthy","tools_count":5}
```

### IPFS not available?

Anchoring will fail without IPFS. Start docker container:

```bash
docker start ipfs
# or create new:
docker run -d --name ipfs -p 5001:5001 -p 8080:8080 ipfs/kubo
```

### XRPL anchoring fails?

Make sure `.env` file has valid `XRPL_SEED`.

---

## Testing

Run basic functionality test:

```bash
python test_mcp_basic.py
```

Expected output:
```
✅ MCP server is healthy
✅ Found 5 tools
✅ All tools working
✅ Logging functional
✅ A2A trace building successful
```

---

## File Locations

- **Session Logs**: `logs/events.jsonl`
- **A2A Traces**: `traces/session-*.json`
- **Configuration**: `.env`

---

## Next Steps

1. Try different prompts
2. Monitor the logs in `logs/events.jsonl`
3. Anchor a session
4. Verify on XRPL Explorer
5. Share your results!

---

**For full documentation, see `README_HACKATHON.md`**
