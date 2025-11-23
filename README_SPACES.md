# 🔐 A2A Trace Anchoring on XRPL - HuggingFace Spaces

**Tamper-proof AI agent logging with MCP (Model Context Protocol) integration**

This is an interactive demo of the A2A Trace Anchoring system, which provides:

- 🔧 **5 Built-in MCP Tools**: Calculator, Clock, Word Counter, String Reverser, Palindrome Checker
- 📊 **Real-time Statistics**: Track tool usage as you chat
- 🔐 **Blockchain Anchoring**: IPFS + XRPL for tamper-proof logs
- 🌐 **Interactive UI**: Chat with AI and see transparent tool logging

## ⚠️ Important Limitations on HuggingFace Spaces

### Limited Functionality

This Spaces deployment has **reduced functionality** compared to local installation:

❌ **IPFS Integration**: Not available (requires Docker)
❌ **XRPL Anchoring**: Not available (requires private keys)
✅ **MCP Tool Calls**: Fully functional
✅ **Session Logging**: Works (logs saved locally in Space)
✅ **A2A Trace Generation**: Works (JSON format)

### What You CAN Do

1. **Chat with AI** using real MCP tools
2. **See tool invocations** in real-time
3. **View statistics** of tool usage
4. **Generate A2A traces** in JSON format
5. **Download traces** for inspection

### What You CANNOT Do

- ❌ Upload traces to IPFS (no Docker)
- ❌ Anchor to XRPL blockchain (no credentials)
- ❌ Verify anchored traces (no blockchain access)

## 💡 For Full Features

To use the complete system with IPFS + XRPL anchoring:

### Local Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/A2A_xrpl_mcp.git
cd A2A_xrpl_mcp

# Start IPFS
docker run -d --name ipfs -p 5001:5001 -p 8080:8080 ipfs/kubo

# Get XRPL Testnet credentials
# Visit: https://xrpl.org/xrp-testnet-faucet.html
echo "XRPL_SEED=sXXXXXXXXXXXXXXXXXXXXXXX" > .env

# Install and run
pip install -r requirements-mcp.txt
./run_mcp_demo.sh
```

📖 **Full Documentation**: [README.md](https://github.com/yourusername/A2A_xrpl_mcp)

## 🔒 Security Notice

⚠️ **This is a demonstration system**

- **No signature validation** - Traces are not cryptographically signed
- **No PII masking** - Do not enter sensitive/personal information
- **Public logging** - All conversations may be logged
- **Test data only** - Use only non-sensitive example data

## 📚 Learn More

- **Project Repository**: [GitHub](https://github.com/yourusername/A2A_xrpl_mcp)
- **A2A Specification**: [a2a_xrpl_spec.md](https://github.com/yourusername/A2A_xrpl_mcp/blob/main/a2a_xrpl_spec.md)
- **XRPL Documentation**: https://xrpl.org/
- **MCP Protocol**: https://modelcontextprotocol.io/

## 📝 Example Prompts

Try these to see MCP tools in action:

- "Calculate 25 * 4"
- "What time is it?"
- "Count words in: hello world this is a test"
- "Reverse the string 'hello world'"
- "Is 'racecar' a palindrome?"
- "Calculate (10 + 5) * 3, then tell me if the result is a palindrome"

## License

Copyright 2025 niikun

Licensed under the Apache License 2.0 - see [LICENSE](LICENSE) file.

---

**Made with ❤️ for transparent AI agent logging**
