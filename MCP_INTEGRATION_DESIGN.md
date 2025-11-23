# MCP-Aware A2A Trace Logger - 統合設計書

## 📋 目次
1. [システム概要](#システム概要)
2. [アーキテクチャ設計](#アーキテクチャ設計)
3. [データフロー](#データフロー)
4. [ログフォーマット設計](#ログフォーマット設計)
5. [新規コンポーネント設計](#新規コンポーネント設計)
6. [既存コンポーネントの再利用](#既存コンポーネントの再利用)
7. [実装ファイル構成](#実装ファイル構成)
8. [セキュリティ考慮事項](#セキュリティ考慮事項)

---

## システム概要

### 目的
AIエージェントがMCP（Model Context Protocol）を介して外部ツールを呼び出す際の全アクションを、改ざん不可能な形で記録・検証する。

### 既存システムとの違い

| 項目 | 既存システム (A2A XRPL) | MCP統合版 |
|------|----------------------|----------|
| ログ対象 | LangChainエージェント実行 | MCPツール呼び出し |
| ログ形式 | A2A形式 (a2a-0.1) | Hybrid (JSON-RPC + A2A メタデータ) |
| UI | なし（CLIデモのみ） | Gradio Webアプリ |
| トリガー | エージェント実行完了時 | ユーザーがボタン押下時 |
| セッション管理 | 自動生成 | Gradio セッション ID |

---

## アーキテクチャ設計

### システム全体図

```
┌─────────────────────────────────────────────────────────────┐
│                      Gradio Web UI                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Chat Input   │  │ Chat Output  │  │ Anchor Button│     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │   LLM API (Claude/GPT) │
         └────────────┬───────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │     MCP Client         │
         │  (mcp_client.py)       │
         └────────────┬───────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │     MCP Server         │
         │  (mcp_server.py)       │
         │                        │
         │  ┌─────────────────┐  │
         │  │  Tool 1: calc   │  │
         │  │  Tool 2: search │  │
         │  │  Tool 3: ...    │  │
         │  └─────────────────┘  │
         └────────────┬───────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │   Hybrid Log Writer    │
         │    (logger.py)         │
         └────────────┬───────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │  logs/events.jsonl     │
         │  (Session-based)       │
         └────────────┬───────────┘
                      │
                      │ (User clicks "Anchor logs")
                      ▼
    ┌─────────────────────────────────────────┐
    │     A2A Trace Converter                 │
    │     (mcp_trace_builder.py)              │
    │                                         │
    │  1. Read events.jsonl                   │
    │  2. Convert to A2A format               │
    │  3. Compute Merkle Root                 │
    └─────────────────┬───────────────────────┘
                      │
                      ▼
    ┌─────────────────────────────────────────┐
    │     AnchorService (既存)                │
    │     (a2a_anchor/anchor_service.py)      │
    │                                         │
    │  ┌─────────────────────────────────┐   │
    │  │  1. IPFS Upload → Get CID       │   │
    │  │  2. XRPL Anchor → Get TX Hash   │   │
    │  │  3. Return Result               │   │
    │  └─────────────────────────────────┘   │
    └─────────────────┬───────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
┌───────────────┐         ┌───────────────┐
│  IPFS Node    │         │  XRPL Testnet │
│  (CID storage)│         │  (TX記録)     │
└───────────────┘         └───────────────┘
```

---

## データフロー

### 1. ツール呼び出しフロー

```
User Input → LLM → MCP Client → MCP Server (Tool) → Result
                                      │
                                      ├─→ Logger (JSON-RPC log)
                                      │
                                      └─→ logs/events.jsonl
```

### 2. アンカリングフロー

```
User clicks "Anchor logs"
    │
    ▼
Read events.jsonl (current session)
    │
    ▼
Convert to A2A format
    │
    ├─→ Compute Merkle Root
    │
    ▼
AnchorService.anchor_trace()
    │
    ├─→ IPFS Upload → CID
    │
    └─→ XRPL Anchor → TX Hash
    │
    ▼
Display result to user
```

---

## ログフォーマット設計

### Hybrid JSON-RPC Log (logs/events.jsonl)

各ツール呼び出しごとに1行のJSONレコード：

```json
{
  "event_id": "evt-uuid-1234",
  "timestamp": "2025-11-23T12:34:56.789Z",
  "session_id": "session-uuid-abcd",
  "actor": "ai_agent",
  "channel": "mcp_tool",
  "jsonrpc_request": {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "calculate",
      "arguments": {"expression": "2+2"}
    },
    "id": 1
  },
  "jsonrpc_response": {
    "jsonrpc": "2.0",
    "result": {
      "content": [
        {
          "type": "text",
          "text": "4"
        }
      ]
    },
    "id": 1
  },
  "status": "success",
  "latency_ms": 123
}
```

### A2A Trace Format (変換後)

セッション全体のログをA2A形式に変換：

```json
{
  "traceVersion": "a2a-0.1",
  "session": {
    "id": "session-uuid-abcd",
    "createdAt": "2025-11-23T12:34:00.000Z",
    "actors": ["user", "ai_agent", "tool:calculate"]
  },
  "model": {
    "name": "claude-3-5-sonnet-20241022",
    "provider": "anthropic"
  },
  "events": [
    {
      "type": "human_message",
      "ts": "2025-11-23T12:34:01.000Z",
      "content": "Calculate 2+2"
    },
    {
      "type": "ai_tool_call",
      "ts": "2025-11-23T12:34:02.000Z",
      "tool": "calculate",
      "args": {"expression": "2+2"},
      "tool_call_id": "call_1"
    },
    {
      "type": "tool_result",
      "ts": "2025-11-23T12:34:03.000Z",
      "tool_call_id": "call_1",
      "content": "4"
    },
    {
      "type": "ai_message",
      "ts": "2025-11-23T12:34:04.000Z",
      "content": "The result is 4."
    }
  ],
  "usage": [
    {
      "turn": 1,
      "input_tokens": 100,
      "output_tokens": 50
    }
  ],
  "hashing": {
    "algorithm": "sha256",
    "chunk_size": 4096,
    "chunkMerkleRoot": "e5d295ed807b...",
    "chunks": ["hash1", "hash2"]
  },
  "signatures": [],
  "redactions": {
    "policy": "pii_mask",
    "masked_fields": []
  }
}
```

---

## 新規コンポーネント設計

### 1. `app.py` - Gradio Webアプリ

**責務:**
- ユーザーとのチャットインターフェース
- LLM APIとMCPクライアントの統合
- セッション管理
- アンカリングボタンの実装

**主要機能:**
```python
def create_gradio_app():
    """Gradio アプリケーションを作成"""

    with gr.Blocks() as app:
        session_state = gr.State({
            "session_id": generate_session_id(),
            "messages": []
        })

        chatbot = gr.Chatbot()
        msg_input = gr.Textbox()
        send_btn = gr.Button("Send")
        anchor_btn = gr.Button("Anchor logs")

        send_btn.click(
            fn=handle_message,
            inputs=[msg_input, session_state],
            outputs=[chatbot, session_state]
        )

        anchor_btn.click(
            fn=anchor_session_logs,
            inputs=[session_state],
            outputs=[gr.Textbox()]
        )

    return app
```

### 2. `logger.py` - Hybrid Log Writer

**責務:**
- MCPツール呼び出しのJSON-RPC形式ログ記録
- A2A形式メタデータの追加
- セッションごとのログファイル管理

**主要クラス:**
```python
class MCPLogger:
    def __init__(self, log_dir: Path = Path("logs")):
        self.log_dir = log_dir
        self.log_dir.mkdir(exist_ok=True)

    def log_tool_call(
        self,
        session_id: str,
        request: dict,
        response: dict,
        latency_ms: float
    ):
        """ツール呼び出しをログに記録"""
        event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "session_id": session_id,
            "actor": "ai_agent",
            "channel": "mcp_tool",
            "jsonrpc_request": request,
            "jsonrpc_response": response,
            "status": "success" if "result" in response else "error",
            "latency_ms": latency_ms
        }

        log_file = self.log_dir / "events.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    def get_session_logs(self, session_id: str) -> List[dict]:
        """特定セッションのログを取得"""
        logs = []
        log_file = self.log_dir / "events.jsonl"

        if not log_file.exists():
            return logs

        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                event = json.loads(line)
                if event["session_id"] == session_id:
                    logs.append(event)

        return logs
```

### 3. `mcp_client.py` - MCPクライアント

**責務:**
- MCPサーバーとの通信
- JSON-RPCリクエスト/レスポンスの処理
- ログ記録との統合

**主要クラス:**
```python
class MCPClient:
    def __init__(self, server_url: str, logger: MCPLogger):
        self.server_url = server_url
        self.logger = logger

    def call_tool(
        self,
        session_id: str,
        tool_name: str,
        arguments: dict
    ) -> dict:
        """ツールを呼び出す"""
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": 1
        }

        start_time = time.time()

        # サーバーに送信
        response = requests.post(
            self.server_url,
            json=request,
            headers={"Content-Type": "application/json"}
        ).json()

        latency_ms = (time.time() - start_time) * 1000

        # ログ記録
        self.logger.log_tool_call(
            session_id=session_id,
            request=request,
            response=response,
            latency_ms=latency_ms
        )

        return response
```

### 4. `mcp_server.py` - MCPサーバー

**責務:**
- ツールの定義と実装
- JSON-RPCエンドポイントの提供
- FastAPI/uvicornベース

**実装例:**
```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

# ツール定義
TOOLS = {
    "calculate": {
        "description": "数式を計算する",
        "parameters": {
            "expression": {"type": "string", "description": "計算式"}
        }
    },
    "get_time": {
        "description": "現在時刻を取得",
        "parameters": {}
    }
}

# ツール実装
def execute_tool(name: str, arguments: dict) -> dict:
    if name == "calculate":
        try:
            result = eval(arguments["expression"])
            return {"content": [{"type": "text", "text": str(result)}]}
        except Exception as e:
            return {"error": str(e)}

    elif name == "get_time":
        from datetime import datetime
        return {
            "content": [{
                "type": "text",
                "text": datetime.now().isoformat()
            }]
        }

    return {"error": f"Unknown tool: {name}"}

@app.post("/")
async def handle_jsonrpc(request: Request):
    """JSON-RPCリクエストを処理"""
    data = await request.json()

    if data.get("method") == "tools/list":
        return JSONResponse({
            "jsonrpc": "2.0",
            "result": {"tools": [
                {"name": name, **info}
                for name, info in TOOLS.items()
            ]},
            "id": data.get("id")
        })

    elif data.get("method") == "tools/call":
        params = data.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        result = execute_tool(tool_name, arguments)

        return JSONResponse({
            "jsonrpc": "2.0",
            "result": result,
            "id": data.get("id")
        })

    return JSONResponse({
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": "Method not found"},
        "id": data.get("id")
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 5. `mcp_trace_builder.py` - A2A変換モジュール

**責務:**
- JSON-RPCログをA2A形式に変換
- Merkle Root計算の統合

**主要クラス:**
```python
from a2a_anchor.trace_schema import TraceJSON, Session, Model, Event, Usage, Hashing
from a2a_anchor.merkle import compute_trace_merkle

class MCPTraceBuilder:
    @staticmethod
    def from_jsonl_logs(
        logs: List[dict],
        model_name: str = "claude-3-5-sonnet",
        provider: str = "anthropic"
    ) -> TraceJSON:
        """JSON-RPCログからA2Aトレースを構築"""

        if not logs:
            raise ValueError("No logs provided")

        session_id = logs[0]["session_id"]
        created_at = logs[0]["timestamp"]

        # アクター収集
        actors = set(["user", "ai_agent"])
        for log in logs:
            if "jsonrpc_request" in log:
                params = log["jsonrpc_request"].get("params", {})
                tool_name = params.get("name")
                if tool_name:
                    actors.add(f"tool:{tool_name}")

        # イベント変換
        events = []
        for log in logs:
            # ツール呼び出しイベント
            if "jsonrpc_request" in log:
                params = log["jsonrpc_request"].get("params", {})
                events.append(Event(
                    type="ai_tool_call",
                    ts=log["timestamp"],
                    tool=params.get("name"),
                    args=params.get("arguments"),
                    tool_call_id=str(log["jsonrpc_request"].get("id"))
                ))

            # ツール結果イベント
            if "jsonrpc_response" in log:
                result = log["jsonrpc_response"].get("result", {})
                content = result.get("content", [])
                text = content[0].get("text") if content else ""

                events.append(Event(
                    type="tool_result",
                    ts=log["timestamp"],
                    tool_call_id=str(log["jsonrpc_response"].get("id")),
                    content=text
                ))

        # トレース構築（Merkle Root計算前）
        trace = TraceJSON(
            session=Session(
                id=session_id,
                createdAt=created_at,
                actors=sorted(list(actors))
            ),
            model=Model(name=model_name, provider=provider),
            events=events,
            usage=[],  # MCPからは取得できない場合は空
            hashing=Hashing()
        )

        # Merkle Root計算
        trace_json = trace.to_json()
        merkle_root, chunk_hashes = compute_trace_merkle(trace_json)

        # ハッシング情報を更新
        trace.hashing.chunkMerkleRoot = merkle_root
        trace.hashing.chunks = chunk_hashes
        trace._merkle_json_cache = trace_json

        return trace
```

---

## 既存コンポーネントの再利用

### そのまま利用できるモジュール

| モジュール | 用途 | 変更不要 |
|-----------|------|---------|
| `a2a_anchor/merkle.py` | Merkle Root計算 | ✅ |
| `a2a_anchor/ipfs_client.py` | IPFS統合 | ✅ |
| `a2a_anchor/xrpl_client.py` | XRPL統合 | ✅ |
| `a2a_anchor/anchor_service.py` | アンカリング統合 | ✅ |
| `a2a_anchor/verify.py` | 検証フロー | ✅ |
| `a2a_anchor/trace_schema.py` | A2Aスキーマ | ✅ |

### 新規作成が必要なモジュール

| モジュール | 用途 |
|-----------|------|
| `app.py` | Gradio UI |
| `logger.py` | MCPログ記録 |
| `mcp_client.py` | MCPクライアント |
| `mcp_server.py` | MCPサーバー |
| `mcp_trace_builder.py` | ログ変換 |

---

## 実装ファイル構成

```
/workspaces/A2A_xrpl_mcp/
├── a2a_anchor/              # 既存（変更不要）
│   ├── __init__.py
│   ├── anchor_service.py
│   ├── ipfs_client.py
│   ├── merkle.py
│   ├── trace_builder.py
│   ├── trace_schema.py
│   ├── verify.py
│   └── xrpl_client.py
├── mcp/                     # 新規ディレクトリ
│   ├── __init__.py
│   ├── app.py              # Gradio UI
│   ├── logger.py           # Hybrid Log Writer
│   ├── mcp_client.py       # MCPクライアント
│   ├── mcp_server.py       # MCPサーバー
│   └── mcp_trace_builder.py # A2A変換
├── logs/                    # 新規（自動生成）
│   └── events.jsonl
├── traces/                  # 既存
│   └── session-*.json
├── requirements-mcp.txt     # MCP用依存関係
└── run_mcp_demo.sh         # 実行スクリプト
```

---

## セキュリティ考慮事項

### 1. ツール実行の安全性
- `eval()` 使用時のサニタイゼーション
- ツール実行のタイムアウト設定
- リソース制限（メモリ、CPU）

### 2. ログのプライバシー
- PII（個人識別情報）の自動マスキング
- 機密情報のフィルタリング
- Redactionポリシーの適用

### 3. アクセス制御
- セッションIDの暗号化
- XRPL秘密鍵の安全な管理（.env）
- IPFS公開範囲の制限

### 4. 改ざん防止
- Merkle Rootによる整合性検証
- XRPLブロックチェーンでの永続化
- タイムスタンプの検証

---

## 次のステップ

1. **プロトタイプ実装**
   - 最小限のMCPサーバー（1-2ツール）
   - 基本的なロギング機能
   - シンプルなGradio UI

2. **統合テスト**
   - IPFS接続テスト
   - XRPL接続テスト
   - エンドツーエンドテスト

3. **機能拡張**
   - 追加ツールの実装
   - UI改善
   - エラーハンドリング強化

4. **ドキュメント整備**
   - ユーザーガイド
   - API仕様書
   - デプロイ手順

---

## 参考資料

- Model Context Protocol: https://modelcontextprotocol.io/
- A2A Trace仕様: [a2a_xrpl_spec.md](./a2a_xrpl_spec.md)
- 既存実装: [demo_full_anchor.py](./demo_full_anchor.py)
