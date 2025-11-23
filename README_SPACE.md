---
title: MCP-Aware A2A Trace Logger
emoji: 🔗
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.0.0
app_file: app_hf.py
pinned: false
license: apache-2.0
tags:
  - mcp
  - blockchain
  - xrpl
  - ipfs
  - ai-transparency
  - audit-trail
  - building-mcp
  - mcp-in-action
---

# 🔗 MCP-Aware A2A Trace Logger

### Transparent, Verifiable, and Tamper-Proof AI Action Logging

🏆 **MCP 1st Birthday Hackathon Submission**

**Tracks:**
- 🛠️ Building MCP
- 🎬 MCP in Action

---

## 🎯 What This Does

This demo shows how AI agent actions via **MCP (Model Context Protocol)** can be:

1. **Logged** in real-time (JSON-RPC + A2A hybrid format)
2. **Converted** to standardized A2A trace format
3. **Anchored** to IPFS + XRPL blockchain for tamper-proof verification

### Try It Out!

1. **Chat with the AI** - Ask it to calculate, check time, count words, etc.
2. **See Tool Calls** - Watch as the AI uses MCP tools automatically
3. **View Statistics** - Monitor session events in real-time
4. **Anchor Logs** - Click the anchor button to create a permanent blockchain record

---

## 🎓 Example Prompts

- "Calculate 25 * 4"
- "What time is it?"
- "Count words in this sentence"
- "Reverse 'hello world'"
- "Is 'racecar' a palindrome?"

---

## 🔬 How It Works

```
User Message
    ↓
AI Decision (which tool to use?)
    ↓
MCP Tool Call (JSON-RPC)
    ↓
Hybrid Logger (JSON-RPC + A2A metadata)
    ↓
logs/events.jsonl
    ↓
[User clicks "Anchor logs"]
    ↓
A2A Trace Format + Merkle Root
    ↓
IPFS Upload (get CID)
    ↓
XRPL Transaction (blockchain record)
    ↓
Verifiable Forever! 🎉
```

---

## 🌟 Key Features

✅ **5 MCP Tools** - calculate, get_time, count_words, reverse_string, check_palindrome
✅ **Real-time Logging** - Every tool call is recorded
✅ **Hybrid Format** - Combines JSON-RPC standard with A2A metadata
✅ **Merkle Proof** - Cryptographic integrity verification
✅ **IPFS Storage** - Distributed, permanent storage
✅ **XRPL Anchoring** - Blockchain record for immutability
✅ **Full Verification** - Anyone can verify from TX hash to original trace

---

## 📊 Architecture

```
Gradio UI ←→ AI Assistant ←→ MCP Server (5 tools)
                                    ↓
                            Hybrid Logger
                                    ↓
                            logs/events.jsonl
                                    ↓
                        [User clicks Anchor]
                                    ↓
                            A2A Trace Builder
                                    ↓
                        IPFS + XRPL Anchoring
                                    ↓
                        Permanent Record ✅
```

---

## 🎥 Demo Video

[Watch the full demo (3 min)](YOUR_VIDEO_LINK)

---

## 📚 Learn More

- **Full Documentation**: [README_HACKATHON.md](README_HACKATHON.md)
- **GitHub Repository**: https://github.com/niikun/A2A_xrpl_mcp
- **MCP Protocol**: https://modelcontextprotocol.io/
- **A2A Trace Spec**: See repository

---

## 🏆 Hackathon Submission

**Tracks:**
- Track 1: Building MCP (Custom MCP server with hybrid logging)
- Track 2: MCP in Action (Interactive Gradio demo with full workflow)

**Category:** Enterprise (Audit & Compliance)

**Innovation:**
- First to combine MCP with blockchain-anchored A2A traces
- Novel hybrid format bridging JSON-RPC and A2A standards
- Triple-layer verification (local + IPFS + blockchain)

---

## ⚠️ Note on Anchoring

**IPFS + XRPL anchoring** is available in the local version with proper setup:

1. IPFS node running locally
2. XRPL Testnet account (get from https://xrpl.org/xrp-testnet-faucet.html)
3. `.env` file with `XRPL_SEED`

**In this HuggingFace Space:**
- ✅ Full UI demonstration
- ✅ MCP tool calling
- ✅ Logging functionality
- ⚠️ IPFS/XRPL anchoring may be limited (requires external services)

For full anchoring features, clone the repository and run locally!

---

## 📄 License

Apache License 2.0

---

**Built with ❤️ for transparent and accountable AI**

#MCP1stBirthday #BuildingMCP #MCPinAction
