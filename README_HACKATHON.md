# 🔗 MCP-Aware A2A Trace Logger

### Transparent, Verifiable, and Tamper-Proof AI Action Logging

[![MCP 1st Birthday](https://img.shields.io/badge/MCP-1st_Birthday-blue)](https://huggingface.co/MCP-1st-Birthday)
[![Track: Building MCP](https://img.shields.io/badge/Track-Building_MCP-green)]()
[![Track: MCP in Action](https://img.shields.io/badge/Track-MCP_in_Action-orange)]()
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-yellow.svg)](LICENSE)

---

## 🏆 HuggingFace Hackathon Submission

<!--
IMPORTANT: Before submitting to the hackathon, complete these steps:

1. ✅ Join the hackathon organization (click "Request to join this org")
2. ✅ Submit this Space to the organization
3. ✅ Add track tags below
4. ✅ Add social media post link
5. ✅ Verify submission before deadline: November 30, 2025, 11:59 PM UTC
-->

**Hackathon:** MCP 1st Birthday Hackathon (November 2025)

**Tracks Entered:**
- `#building-with-mcp` - Custom MCP server with 5 tools + hybrid logging system
- `#mcp-in-action` - Real-world application: Blockchain-anchored AI audit trails

**Tag:** `building-mcp-track-enterprise`

**Demo Video:** https://www.youtube.com/watch?v=skF58ABgoE8

**Social Media Posts:**
- LinkedIn: https://www.linkedin.com/posts/kawata-akimoto-711320228_mcp-aitransparency-a2a-activity-7398355559814610944-hGvC
- X (Twitter): https://x.com/niiniikun/status/1992590732662857794


**Team:** niikun (Solo)

**Demo:** This Space

**Full Source:** https://github.com/niikun/A2A_xrpl_mcp

---

## 🎯 Problem Statement

As AI agents become more autonomous and powerful, we face critical challenges:

- **Lack of Transparency**: Users can't see what tools AI agents actually call
- **No Accountability**: No verifiable record of AI actions
- **Trust Issues**: How can we prove an AI agent did (or didn't) perform certain actions?
- **Audit Requirements**: Regulated industries need tamper-proof audit trails

**Current solutions are insufficient:**
- Simple logs can be edited or deleted
- Centralized databases can be compromised
- No cryptographic proof of integrity

---

## 💡 Our Solution

**MCP-Aware A2A Trace Logger** creates a complete chain of trust for AI agent actions:

```
AI Tool Call → MCP Logging → A2A Format → Merkle Root → IPFS → XRPL Blockchain
                                                             ↓
                                            Permanent, Verifiable Record
```

### Key Features

✅ **Real-time Logging** - Every MCP tool invocation is logged in hybrid JSON-RPC format
✅ **A2A Compliance** - Converts logs to standardized A2A trace format
✅ **Merkle Proof** - Cryptographic integrity verification via Merkle Root
✅ **IPFS Storage** - Distributed, permanent storage with Content ID (CID)
✅ **XRPL Anchoring** - Blockchain record on XRPL Testnet for immutability
✅ **Full Verification** - Anyone can verify the complete chain from TX hash to original trace

---

## 🏆 Hackathon Tracks

This project qualifies for **both tracks**:

### 🛠️ Track 1: Building MCP
- **Custom MCP Server** with 5 practical tools (calculate, time, word count, reverse, palindrome)
- **Hybrid Logging Architecture** combining JSON-RPC and A2A metadata
- **Transparent Tool Invocation** - All MCP calls are automatically logged

### 🎬 Track 2: MCP in Action
- **Interactive Gradio UI** showing AI agent in action
- **Real-time Statistics** for session monitoring
- **One-Click Anchoring** to IPFS + XRPL
- **Complete Demonstration** of planning → execution → verification

---

## 🎥 Demo Video

[**Watch the 3-minute demo here**](https://www.youtube.com/watch?v=skF58ABgoE8)

🎬 Demo shows:
1. AI agent using MCP tools to solve user requests
2. Real-time logging of all tool calls
3. Converting logs to A2A format
4. Anchoring to IPFS and XRPL
5. Verifying the complete chain on blockchain

---

## 🚀 Quick Start

### Prerequisites

```bash
# 1. IPFS (for distributed storage)
docker run -d --name ipfs -p 5001:5001 -p 8080:8080 ipfs/kubo

# 2. XRPL Testnet Account
# Visit: https://xrpl.org/xrp-testnet-faucet.html
# Get your seed and add to .env:
echo "XRPL_SEED=sXXXXXXXXXXXXXXXXXXXXXXX" > .env
```

### Installation

```bash
# Clone repository
git clone https://github.com/niikun/A2A_xrpl_mcp
cd A2A_xrpl_mcp

# Install dependencies
pip install -r requirements-mcp.txt

# Run the demo
./run_mcp_demo.sh
```

### Access the UI

Open your browser to: **http://localhost:7860**

---

## 📋 How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Gradio Web UI (Port 7860)                   │
│  User Chat ←→ AI Assistant ←→ MCP Tool Calls            │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
      ┌───────────────────────┐
      │   MCP Server (8000)   │
      │  - calculate          │
      │  - get_time           │
      │  - count_words        │
      │  - reverse_string     │
      │  - check_palindrome   │
      └───────────┬───────────┘
                  │
                  ▼
      ┌───────────────────────┐
      │   Hybrid Logger       │
      │  JSON-RPC + A2A Meta  │
      └───────────┬───────────┘
                  │
                  ▼
         logs/events.jsonl
                  │
    (User clicks "Anchor logs")
                  │
                  ▼
      ┌───────────────────────┐
      │  A2A Trace Builder    │
      │  - Convert format     │
      │  - Compute Merkle     │
      └───────────┬───────────┘
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
   ┌─────────┐       ┌─────────┐
   │  IPFS   │       │  XRPL   │
   │  (CID)  │       │  (TX)   │
   └─────────┘       └─────────┘
```

### Data Flow

1. **User Input** → AI processes request
2. **Tool Detection** → AI decides which MCP tool to call
3. **MCP Call** → Tool executes via JSON-RPC
4. **Logging** → Request + Response logged in hybrid format
5. **Response** → User sees the result
6. **Anchoring** (on demand):
   - Logs → A2A format conversion
   - Merkle Root computation
   - IPFS upload → Get CID
   - XRPL transaction → Get TX hash
7. **Verification** → Anyone can verify via XRPL Explorer

---

## 🔍 Example Usage

### Chat Interaction

```
User: Calculate 25 * 4
AI: I calculated that for you: Result: 100.0
```

**Behind the scenes:**
```json
{
  "event_id": "evt-abc123",
  "timestamp": "2025-11-23T12:00:00Z",
  "session_id": "session-xyz789",
  "actor": "ai_agent",
  "channel": "mcp_tool",
  "jsonrpc_request": {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "calculate",
      "arguments": {"expression": "25 * 4"}
    }
  },
  "jsonrpc_response": {
    "result": {"content": [{"type": "text", "text": "Result: 100.0"}]}
  },
  "status": "success",
  "latency_ms": 12.34
}
```

### Anchoring Result

```
✅ Anchoring Complete!

Session ID: session-xyz789
IPFS CID: QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG
IPFS URL: ipfs://QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG
XRPL TX Hash: 8313F6124E4FEAEB545932DED7FB46CFD2E85203ED6756C9EE58B4943F01AA21
Ledger Index: 12180011
Merkle Root: e5d295ed807b...

XRPL Explorer:
https://testnet.xrpl.org/transactions/8313F6124E4FEAEB545932DED7FB46CFD2E85203ED6756C9EE58B4943F01AA21
```

---

## 🎓 Technical Innovation

### 1. Hybrid Log Format

Combines **JSON-RPC standard** with **A2A metadata**:

```json
{
  "jsonrpc_request": {...},    // Standard JSON-RPC
  "jsonrpc_response": {...},   // Standard JSON-RPC
  "timestamp": "...",           // A2A metadata
  "session_id": "...",         // A2A metadata
  "actor": "ai_agent",         // A2A metadata
  "status": "success",         // A2A metadata
  "latency_ms": 123            // A2A metadata
}
```

### 2. Merkle Root Verification

- Chunks trace into 4KB segments
- Computes SHA-256 hash of each chunk
- Builds Merkle tree
- Root hash proves integrity of entire trace

### 3. Triple-Layer Anchoring

- **Layer 1**: Local file (`traces/session-*.json`)
- **Layer 2**: IPFS distributed storage (CID)
- **Layer 3**: XRPL blockchain (TX hash)

Anyone with the TX hash can:
1. Query XRPL → Get memo with CID + Merkle Root
2. Fetch from IPFS using CID → Get full trace
3. Recalculate Merkle Root → Compare with anchored value
4. **Verify integrity** ✅

---

## 🌟 Use Cases

### Enterprise Audit & Compliance
- Financial institutions tracking AI trading decisions
- Healthcare providers auditing AI diagnostic assistance
- Legal firms documenting AI research processes

### Research & Development
- AI safety research requiring verifiable experiment logs
- Academic papers with reproducible AI agent behavior
- Benchmarking AI tool usage patterns

### Consumer Trust
- Transparent AI assistants showing exactly what tools they use
- Privacy-conscious users verifying data handling
- Accountability for autonomous AI agents

---

## 📊 Project Structure

```
A2A_xrpl_mcp/
├── mcp/                          # NEW: MCP Integration
│   ├── __init__.py
│   ├── app.py                    # Gradio UI application
│   ├── logger.py                 # Hybrid log writer
│   ├── mcp_client.py             # MCP client with logging
│   ├── mcp_server.py             # MCP server (5 tools)
│   └── mcp_trace_builder.py      # A2A conversion
│
├── a2a_anchor/                   # Existing: A2A Infrastructure
│   ├── anchor_service.py         # IPFS + XRPL integration
│   ├── ipfs_client.py            # IPFS interaction
│   ├── xrpl_client.py            # XRPL interaction
│   ├── merkle.py                 # Merkle Root computation
│   ├── trace_schema.py           # A2A format schema
│   └── verify.py                 # Verification module
│
├── logs/                         # Generated logs
│   └── events.jsonl              # Session logs
│
├── traces/                       # Generated traces
│   └── session-*.json            # A2A format traces
│
├── requirements-mcp.txt          # Dependencies
├── run_mcp_demo.sh              # Startup script
├── README_HACKATHON.md          # This file
└── .env                         # Configuration (XRPL_SEED)
```

---

## 🔬 Testing & Verification

### Run Tests

```bash
# Test IPFS connection
python -m pytest tests/test_ipfs.py

# Test XRPL connection
python -m pytest tests/test_xrpl.py

# Test end-to-end integration
python -m pytest tests/test_xrpl.py::test_full_integration_anchor_and_verify
```

### Manual Verification

```bash
# 1. Run a session and anchor it
./run_mcp_demo.sh

# 2. Get TX hash from UI after anchoring

# 3. Verify from command line
python -c "
from a2a_anchor.xrpl_client import create_xrpl_client
from a2a_anchor.ipfs_client import create_ipfs_client
from a2a_anchor.verify import TraceVerifier
import os
from dotenv import load_dotenv

load_dotenv()

xrpl = create_xrpl_client(
    'https://s.altnet.rippletest.net:51234',
    seed=os.getenv('XRPL_SEED'),
    network='testnet'
)
ipfs = create_ipfs_client()
verifier = TraceVerifier(xrpl, ipfs)

result = verifier.verify('YOUR_TX_HASH')
print(f'✓ Verified: {result.verified}')
print(f'Merkle Match: {result.expected_root == result.computed_root}')
"
```

---

## 🛣️ Roadmap

### Current Features (MVP)
- ✅ MCP server with 5 tools
- ✅ Hybrid logging (JSON-RPC + A2A)
- ✅ Gradio UI
- ✅ IPFS + XRPL anchoring
- ✅ Full verification chain

### Future Enhancements
- [ ] Support for more MCP tools (web search, database, APIs)
- [ ] Real LLM integration (Claude, GPT-4)
- [ ] Digital signatures (EIP-191-like)
- [ ] PII redaction and privacy features
- [ ] Multi-session trace aggregation
- [ ] XRPL EVM sidechain + EAS compatibility
- [ ] ZK proofs for content-private verification
- [ ] Browser extension for easy verification

---

## 🏅 Why This Project Wins

### Innovation
- **First** to combine MCP with blockchain-anchored A2A traces
- **Novel hybrid format** bridging JSON-RPC and A2A standards
- **Triple-layer** verification (local + IPFS + blockchain)

### Practicality
- **Actually works** - Full end-to-end implementation
- **Easy to use** - One-click anchoring via Gradio UI
- **Production-ready architecture** - Modular, testable, documented

### Impact
- **Addresses real needs** - Enterprise audit, research reproducibility, consumer trust
- **Open source** - Apache 2.0 license for community adoption
- **Standards-based** - Uses MCP, A2A, IPFS, XRPL standards

### Technical Excellence
- **Clean code** - Well-structured, documented, tested
- **Security-first** - Safe eval, proper error handling
- **Scalable design** - Modular components, extensible architecture

---

## 👥 Team

**niikun** - Full-stack developer passionate about AI transparency and blockchain

- GitHub: [@niikun](https://github.com/niikun)
- Project: A2A Trace Anchoring on XRPL
- Track: Building MCP + MCP in Action

---

## 📄 License

Apache License 2.0 - see [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

- **Anthropic** for Claude and MCP protocol
- **Gradio** for the amazing UI framework
- **XRPL** for reliable blockchain infrastructure
- **IPFS** for distributed storage
- **MCP 1st Birthday Hackathon** for the opportunity

---

## 🔗 Links

- **Project Repository**: https://github.com/niikun/A2A_xrpl_mcp
- **Demo Video**: https://www.youtube.com/watch?v=skF58ABgoE8
- **Interactive Demo**: https://niikun.net/A2A_demo.html
- **XRPL Explorer Example**: https://testnet.xrpl.org/transactions/8313F6124E4FEAEB545932DED7FB46CFD2E85203ED6756C9EE58B4943F01AA21
- **MCP Specification**: https://modelcontextprotocol.io/
- **A2A Trace Spec**: [a2a_xrpl_spec.md](./a2a_xrpl_spec.md)

---

## 📧 Contact

Questions or feedback? Open an issue or reach out!

**Built with ❤️ for transparent and accountable AI**

#MCP1stBirthday #BuildingMCP #MCPinAction #AI #Blockchain #Transparency
