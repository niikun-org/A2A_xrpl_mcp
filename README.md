# A2A Trace Anchoring on XRPL

**An open-source system for tamper-proof recording and verification of AI agent actions**

**AIエージェントの全行動を、改ざん不可能な形で記録・検証できるオープンソースシステム**

📖 **[日本語版はこちら / Japanese Version](README_JA.md)**

## Presentation

- View the PDF presentation here:

https://acrobat.adobe.com/id/urn:aaid:sc:AP:39dc90b8-05b8-4001-923f-ee15bc38b82e

- Try the interactive demo:

https://niikun.net/A2A_demo.html

## What It Does

This project records execution traces of LangChain agents (haiku_agent) with:

1. **Standardization**: Recording in A2A format (a2a-0.1) JSON
2. **Integrity Guarantee**: Hash verification via Merkle Root
3. **Distributed Storage**: Storage on IPFS (InterPlanetary File System)
4. **Blockchain Recording**: Recording on XRPL ledger for tamper verification

## Current Implementation Status

### ✅ Phase 1 Complete
- Convert LangChain agent execution logs to A2A format
- Integrity verification via Merkle Root calculation
- Local JSON file storage

### ✅ Phase 2 Complete
- IPFS integration (save traces to IPFS, get CID)
- IPFS verification (retrieve trace by CID, verify Merkle Root)

### ✅ Phase 3 Complete (Full Implementation!)
- XRPL integration (anchoring to Testnet, Memo recording)
- Complete verification flow (XRPL → IPFS → Merkle Root verification)
- Integrated service (AnchorService) for batch processing
- End-to-end verification system

## How to Run Demos

### 🌐 Interactive Web Demo (Most User-Friendly!)

Open the following HTML files in your browser:

#### 1. See the System in Action
```bash
open demo_interactive.html
```
**[demo_interactive.html](demo_interactive.html)** - Animated explanation demo
- 🎬 6-step animation
- ▶️ Auto-play feature
- ⌨️ Keyboard controls (arrow keys, space bar)
- 📊 Real-time progress bar

#### 2. View Actual Trace Files
```bash
open trace_viewer.html
```
**[trace_viewer.html](trace_viewer.html)** - Trace file visualization tool
- 📁 Drag & drop JSON files
- 📊 Display statistics
- ⏱️ Event timeline
- 🔐 Merkle Root verification info

---

### 🎓 Interactive Terminal Demo

```bash
uv run demo_simple_explanation.py
```

**This demo interactively explains the A2A trace anchoring mechanism:**
- ✨ Step-by-step understanding
- 📊 Visual diagrams
- 💡 Real-world use cases
- 🔍 Detailed phase explanations

📖 **Detailed illustrated documentation**: [EXPLANATION.md](./EXPLANATION.md)

---

### Phase 1: Local Storage Only

```bash
uv run demo_haiku_trace.py
```

### Phase 2: IPFS Integration Demo

#### 1. Start IPFS Node

```bash
# Fresh start
docker run -d --name ipfs -p 5001:5001 -p 8080:8080 ipfs/kubo
```

**Note:** Troubleshooting if IPFS container already exists:

```bash
# Check container status
docker ps -a | grep ipfs

# Restart if stopped
docker start ipfs

# If errors occur, remove and recreate
docker rm -f ipfs
docker run -d --name ipfs -p 5001:5001 -p 8080:8080 ipfs/kubo
```

#### 2. Run Demo

```bash
uv run demo_haiku_ipfs.py
```

### Phase 3: Full Anchoring (IPFS + XRPL)

#### 1. Start IPFS Node

```bash
# Check container status
docker ps -a | grep ipfs

# Restart if stopped
docker start ipfs

# Create new if doesn't exist
docker run -d --name ipfs -p 5001:5001 -p 8080:8080 ipfs/kubo
```

**Note:** If you already started IPFS in Phase 2, you can use the same instance.

#### 2. Get XRPL Testnet Account

1. Visit [XRPL Testnet Faucet](https://xrpl.org/xrp-testnet-faucet.html)
2. Click "Generate" to create a Testnet account
3. Add the displayed `Secret` (seed) to your `.env` file:

```bash
XRPL_SEED=sXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

#### 3. Run Demo

```bash
uv run demo_full_anchor.py
```

### Expected Output

#### Phase 1 (Local Storage Only)

```
=== Running haiku_agent ===
checking haiku it has 3 lines.:
 Field lights bite the dusk
Fans roar, drums call through the stands
Glory tastes of rain

=== Agent Result ===
Messages: 20 messages

=== Building A2A Trace ===
Session ID: session-1984a1a429f6
Model: gpt-5-nano-2025-08-07
Events: 20
Actors: assistant, tool:check_haiku_lines, user
Total tokens: 22082 (input: 4229, output: 17853)
Merkle Root: 43b10e78082bfd87c859ca55766d4abfebda42e5686c63509754b641ed93a9f5
Chunks: 2

=== Trace saved to: traces/session-XXXXX.json ===
```

#### Phase 2 (IPFS Integration)

In addition to Phase 1 output:

```
=== Phase 2: Uploading to IPFS ===
Connected to IPFS node (version: 0.x.x)
✓ Trace uploaded to IPFS
  CID: bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi
  IPFS URL: ipfs://bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi
  Gateway URL: http://127.0.0.1:8080/ipfs/bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi
✓ Content pinned to prevent garbage collection

=== Verifying IPFS retrieval ===
✓ Merkle Root verification: PASSED
  Expected: 43b10e78082bfd87c859ca55766d4abfebda42e5686c63509754b641ed93a9f5
  Retrieved: 43b10e78082bfd87c859ca55766d4abfebda42e5686c63509754b641ed93a9f5

=== Phase 2 Complete ===
Local file: traces/session-XXXXX.json
IPFS CID: bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi
```

#### Phase 3 (Full Anchoring)

In addition to Phase 1 and 2 output:

```
=== Step 5: Anchoring to IPFS + XRPL ===
Uploading to IPFS...
Anchoring to XRPL Testnet...
(This may take 4-5 seconds for ledger validation...)

✓ Anchoring Complete!
  Session ID: session-c6258f2777c2
  IPFS CID: QmSYKU3iV1u53RP2jCbQV9coDJRLJYoiNJTdLyDUTYGGHT
  IPFS URL: ipfs://QmSYKU3iV1u53RP2jCbQV9coDJRLJYoiNJTdLyDUTYGGHT
  Gateway URL: http://127.0.0.1:8080/ipfs/QmSYKU3iV1u53RP2jCbQV9coDJRLJYoiNJTdLyDUTYGGHT
  XRPL TX Hash: 8313F6124E4FEAEB545932DED7FB46CFD2E85203ED6756C9EE58B4943F01AA21
  Ledger Index: 12180011
  Merkle Root: e5d295ed807b7881eb2e2e977a04e9922c991f736dbe80a059846aa5e1aef673
  Timestamp: 1762610214

=== Step 6: Verifying Anchored Trace ===
Verifying transaction: 8313F6124E4FEAEB545932DED7FB46CFD2E85203ED6756C9EE58B4943F01AA21
1. Retrieving memo from XRPL...
2. Fetching trace from IPFS...
3. Recalculating Merkle Root...
4. Comparing with anchored root...

======================================================================
✓ VERIFICATION PASSED
======================================================================
  Session ID: session-c6258f2777c2
  IPFS CID: QmSYKU3iV1u53RP2jCbQV9coDJRLJYoiNJTdLyDUTYGGHT
  Expected Root: e5d295ed807b7881eb2e2e977a04e9922c991f736dbe80a059846aa5e1aef673
  Computed Root: e5d295ed807b7881eb2e2e977a04e9922c991f736dbe80a059846aa5e1aef673
  Match: ✓ YES
  Model: gpt-5-nano-2025-08-07
  Events: 8
  Chunks: 1

======================================================================
SUCCESS: Complete A2A Trace Anchoring
======================================================================

Local File: traces/session-c6258f2777c2.json
IPFS CID: QmSYKU3iV1u53RP2jCbQV9coDJRLJYoiNJTdLyDUTYGGHT
XRPL TX: 8313F6124E4FEAEB545932DED7FB46CFD2E85203ED6756C9EE58B4943F01AA21

Explore on XRPL:
  https://testnet.xrpl.org/transactions/8313F6124E4FEAEB545932DED7FB46CFD2E85203ED6756C9EE58B4943F01AA21
```

## Verifying Traces

#### Check Local File

```bash
cat traces/session-*.json | jq .
```

#### Retrieve and Verify from IPFS

```bash
# Verify with Python (recommended)
uv run python -c "from a2a_anchor.ipfs_client import create_ipfs_client; client = create_ipfs_client(); trace = client.get_json('<CID>'); print(f\"Session: {trace['session']['id']}\"); print(f\"Merkle Root: {trace['hashing']['chunkMerkleRoot']}\")"

# Or via IPFS gateway (if port 8080 is exposed)
curl http://127.0.0.1:8080/ipfs/<CID> | jq .

# Using public IPFS gateway
curl https://ipfs.io/ipfs/<CID> | jq .
```

**Note:** When using GitHub Codespaces:
1. Open the "Ports" tab in VSCode
2. Find port 8080 and change "Visibility" to "Public"
3. Or access IPFS directly from Python (command above)

#### Full Verification from XRPL Transaction

```bash
# Verify from transaction hash (actual example)
uv run python -c "
from a2a_anchor.xrpl_client import create_xrpl_client
from a2a_anchor.ipfs_client import create_ipfs_client
from a2a_anchor.verify import TraceVerifier
import os
from dotenv import load_dotenv

load_dotenv()

xrpl = create_xrpl_client(
    os.getenv('XRPL_NODE_URL', 'https://s.altnet.rippletest.net:51234'),
    seed=os.getenv('XRPL_SEED'),
    network='testnet'
)
ipfs = create_ipfs_client()
verifier = TraceVerifier(xrpl, ipfs)

# Actual transaction example
tx_hash = '8313F6124E4FEAEB545932DED7FB46CFD2E85203ED6756C9EE58B4943F01AA21'
result = verifier.verify(tx_hash)

print(f'Verified: {result.verified}')
print(f'Session ID: {result.session_id}')
print(f'IPFS CID: {result.cid}')
print(f'Merkle Root Match: {result.expected_root == result.computed_root}')
"
```

## Real Verification Example

Here's an actual trace recorded on XRPL Testnet:

### Verifiable Transaction

**Transaction Hash**: `8313F6124E4FEAEB545932DED7FB46CFD2E85203ED6756C9EE58B4943F01AA21`

- **XRPL Explorer**: https://testnet.xrpl.org/transactions/8313F6124E4FEAEB545932DED7FB46CFD2E85203ED6756C9EE58B4943F01AA21
- **Ledger Index**: 12180011
- **Session ID**: session-c6258f2777c2
- **IPFS CID**: QmSYKU3iV1u53RP2jCbQV9coDJRLJYoiNJTdLyDUTYGGHT
- **Merkle Root**: e5d295ed807b7881eb2e2e977a04e9922c991f736dbe80a059846aa5e1aef673
- **Model**: gpt-5-nano-2025-08-07
- **Events**: 8 (AI agent and tool interactions)

### Verify This Transaction

```bash
# 1. Retrieve trace data from IPFS
curl http://127.0.0.1:8080/ipfs/QmSYKU3iV1u53RP2jCbQV9coDJRLJYoiNJTdLyDUTYGGHT | jq .

# 2. Run complete verification in Python
uv run python -c "
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

result = verifier.verify('8313F6124E4FEAEB545932DED7FB46CFD2E85203ED6756C9EE58B4943F01AA21')
print(f'✓ Verified: {result.verified}')
print(f'Session: {result.session_id}')
print(f'Merkle Match: {result.expected_root == result.computed_root}')
"
```

## Trace File Contents

Generated JSON includes:

```json
{
  "traceVersion": "a2a-0.1",
  "session": {
    "id": "session-1984a1a429f6",
    "createdAt": "2025-11-02T15:16:07.325139+00:00",
    "actors": ["assistant", "tool:check_haiku_lines", "user"]
  },
  "model": {
    "name": "gpt-5-nano-2025-08-07",
    "provider": "openai"
  },
  "events": [
    {"type": "human_message", "content": "please write a poem.", ...},
    {"type": "ai_tool_call", "tool": "check_haiku_lines", ...},
    {"type": "tool_result", "content": "Correct!!", ...}
  ],
  "usage": [
    {"turn": 1, "input_tokens": 171, "output_tokens": 1391}
  ],
  "hashing": {
    "algorithm": "sha256",
    "chunkMerkleRoot": "43b10e78082bfd...",
    "chunks": ["hash1", "hash2"]
  }
}
```

## Project Structure

```
.
├── a2a_anchor/              # A2A anchoring library
│   ├── __init__.py
│   ├── trace_schema.py      # A2A JSON schema (Pydantic)
│   ├── trace_builder.py     # LangChain result → A2A conversion
│   ├── merkle.py            # Merkle Root calculation
│   ├── ipfs_client.py       # IPFS integration (Phase 2)
│   ├── xrpl_client.py       # XRPL integration (Phase 3)
│   ├── anchor_service.py    # Integrated anchoring service (Phase 3)
│   └── verify.py            # Verification module (Phase 3)
├── tests/                   # Test code
│   ├── test_ipfs.py         # IPFS client tests
│   └── test_xrpl.py         # XRPL client tests
├── demo_haiku_trace.py      # Demo: Phase 1 (local storage)
├── demo_haiku_ipfs.py       # Demo: Phase 2 (IPFS integration)
├── demo_full_anchor.py      # Demo: Phase 3 (full anchoring)
├── haiku_agent.py           # LangChain agent that generates Haiku
├── traces/                  # Generated trace files
└── a2a_xrpl_spec.md        # Specification
```

## Recorded Information

- **User Messages**: Input to agent
- **AI Messages**: Agent responses
- **Tool Calls**: Tool executions like check_haiku_lines
- **Tool Results**: Tool execution results
- **Metadata**: Model name, token usage, timestamps
- **Integrity Verification**: Merkle Root (for tamper detection)

## Why This Is Needed

### Problem
- LLM agent execution logs can be tampered with
- No way to prove who executed which tools and how many times
- Need to prove execution history for audits and compliance

### Solution (✅ Implemented)
1. **Standardization**: Record in human-readable A2A format
2. **Hashing**: Guarantee content integrity with Merkle Root
3. **Distributed Storage**: Permanent and distributed storage on IPFS
4. **Blockchain Recording**: Record CID + Merkle Root on XRPL Testnet
5. **Complete Verification**: Verifiable from transaction hash to original trace

## Running Tests

### IPFS Tests

```bash
# Start IPFS node
docker run -d --name ipfs -p 5001:5001 -p 8080:8080 ipfs/kubo

# Run tests
uv run pytest tests/test_ipfs.py -v

# Skip if IPFS unavailable
uv run pytest -k "not ipfs"
```

### XRPL Tests

```bash
# Set XRPL_SEED in .env file

# Run tests
uv run pytest tests/test_xrpl.py -v

# Skip if XRPL unavailable
uv run pytest -k "not xrpl"
```

### Integration Tests

```bash
# Requires both IPFS + XRPL
uv run pytest tests/test_xrpl.py::test_full_integration_anchor_and_verify -v
```

## Implemented Features

### Phase 1: Local Trace Recording
- ✅ Capture LangChain agent execution logs
- ✅ Convert to A2A format (a2a-0.1)
- ✅ Calculate Merkle Root
- ✅ Save JSON file

### Phase 2: IPFS Integration
- ✅ IPFS client implementation
- ✅ Upload traces to IPFS
- ✅ CID retrieval and pinning
- ✅ Retrieve from IPFS and verify

### Phase 3: XRPL Integration
- ✅ XRPL client implementation
- ✅ Send transactions to XRPL Testnet
- ✅ Record CID + Merkle Root in Memo field
- ✅ Integrated anchoring service (AnchorService)
- ✅ Complete verification flow (verify.py)
- ✅ End-to-end testing

## Architecture

```
1. LangChain agent execution
   ↓
2. TraceBuilder: messages → A2A JSON
   ↓
3. Merkle calculation: JSON → chunking → Merkle Root
   ↓
4. IPFS storage: JSON → get CID → Pin
   ↓
5. XRPL recording: Payment TX + Memo {cid, root, meta}
   ↓
6. Verification: TX Hash → Memo → CID → IPFS → JSON → recalculate Merkle Root → compare
```

## Future Extensions

The following features are in the spec but not yet implemented in this MVP:

- XRPL EVM sidechain with EAS compatibility
- ZK proofs for content-private verification
- Next.js viewer with timeline display
- Signature functionality (EIP-191-like)
- Redaction (PII masking) features
- CLI tool (`a2a` command)

## References

- Detailed specification: [a2a_xrpl_spec.md](./a2a_xrpl_spec.md)
- XRPL: https://xrpl.org/
- IPFS: https://ipfs.tech/

## License

Copyright 2025 niikun

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
