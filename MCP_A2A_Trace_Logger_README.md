# MCP-Aware A2A Trace Logger
### Transparent MCP Tool Invocation Logging with Merkle Root, IPFS, and XRPL Anchoring  
*Built with Python + Gradio + MCP + A2A Trace Anchoring Module*

---

## 🚀 Overview

This project demonstrates **transparent and verifiable logging of AI’s external actions** by tracing all **MCP (Model Context Protocol) tool invocations**.

When the AI interacts with external tools via MCP—such as calling APIs, querying XRPL, or fetching web data—the system records each tool call in a **Hybrid Log**:

- Raw **JSON-RPC** request & response  
- + Minimal A2A-style metadata (timestamp, session ID, status, latency)

All logs are saved in `logs/events.jsonl`.

At the end of a session, the user can press **“Anchor logs”**, and the system will:

1. Compute a **Merkle Root** of the session log  
2. Upload the full log to **IPFS** (returns CID)  
3. Anchor the Merkle Root + CID to **XRPL Testnet** as an immutable record  

👉 *This creates an end-to-end verifiable chain for AI external actions.*

---

## 🎯 Motivation

AI systems are increasingly required to provide:

- **Transparency**
- **Traceability**
- **Accountability**
- **Third-party verifiable logs**

MCP defines how AI agents call tools.  
**A2A Trace** defines how AI external actions should be logged.

This project connects both worlds:

> **MCP → Hybrid Log → Merkle Root → IPFS → XRPL**

Making AI actions tamper-proof and independently verifiable.

---

## 🏗 Architecture

```
┌───────────┐       ┌──────────────┐       ┌────────────────┐
│  Gradio   │──────▶│   LLM API    │──────▶│   MCP Client   │
└───────────┘       └──────────────┘       └────────────────┘
                                                      │
                                                      ▼
                                             ┌────────────────┐
                                             │   MCP Server   │
                                             │ (Python tools) │
                                             └────────────────┘
                                                      │
                                                      ▼
                                      Hybrid JSON-RPC Log Writer
                                                      │
                                                      ▼
                                        logs/events.jsonl (session)
                                                      │
                                                      ▼
                           ┌──────────────┬──────────────┬──────────────┐
                           │ Merkle Root  │   IPFS CID    │ XRPL Tx Hash │
                           └──────────────┴──────────────┴──────────────┘
```

---

## 📦 Directory Structure

```
mcp-a2a/
 ├── app.py
 ├── logger.py
 ├── mcp_client.py
 ├── mcp_server.py
 ├── anchor_adapter.py
 ├── logs/
 │    └── events.jsonl
 ├── requirements.txt
 └── README.md
```

---

## 🧩 Hybrid Logging Format

```
{
  "event_id": "uuid-xxxx",
  "timestamp": "2025-11-23T12:34:56Z",
  "session_id": "session-uuid-1234",
  "actor": "ai_agent",
  "channel": "mcp_tool",
  "jsonrpc_request": {...},
  "jsonrpc_response": {...},
  "status": "success",
  "latency_ms": 123
}
```

---

## 📋 requirements.txt

```
gradio
fastapi
uvicorn
requests
```

---

## 🧪 How to Run

```
pip install -r requirements.txt
python mcp_server.py
python app.py
```

---

## 🏁 Summary

Verifiable MCP tool-call logging + Merkle Root + IPFS + XRPL anchoring.
Ideal for AI transparency, accountability, and compliance scenarios.
