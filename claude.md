# A2A Trace Anchoring - Technical Context for Claude

このドキュメントは、AIアシスタント（Claude等）がこのプロジェクトを理解し、開発を継続するための技術的なコンテキストです。

## プロジェクト概要

LangChainベースのLLMエージェントの実行トレースを、改ざん検証可能な形でIPFS + XRPLに記録するシステムの実装です。

### 目的
- LLMエージェントの実行履歴を **標準化された形式** (A2A) で記録
- **Merkle Root** によるトレースの完全性保証
- **IPFS** による分散ストレージ（低コスト、コンテンツアドレス指定）
- **XRPL台帳** によるタイムスタンプと公開検証の実現

## 技術スタック

### 実装済み（Phase 1）
- **Python 3.x** + **Pydantic**: スキーマ定義と検証
- **LangChain**: エージェントフレームワーク
- **hashlib**: SHA256によるMerkle Root計算

### 未実装（Phase 2/3）
- **IPFS**: `ipfshttpclient` または HTTP API経由でトレースを保存
- **XRPL**: `xrpl-py` ライブラリでTestnetにトランザクション送信

## アーキテクチャ

```
1. LangChainエージェント実行
   ↓
2. TraceBuilder: messages → A2A JSON
   ↓
3. Merkle計算: JSON → チャンク化 → Merkle Root
   ↓
4. [Phase 2] IPFS保存: JSON → CID取得
   ↓
5. [Phase 3] XRPL記録: Memo {cid, root, meta}
   ↓
6. 検証: tx_hash → Memo → CID → JSON取得 → Root再計算 → 一致確認
```

## ディレクトリ構造

```
a2a_anchor/
├── __init__.py           # パッケージ初期化
├── trace_schema.py       # A2A JSONスキーマ（Pydantic models）
├── trace_builder.py      # LangChain result → TraceJSON 変換
├── merkle.py             # Merkle Root計算ロジック
├── ipfs_client.py        # [未実装] IPFS API ラッパー
├── xrpl_client.py        # [未実装] XRPL トランザクション送信
├── anchor_service.py     # [未実装] 全体統合サービス
└── verify.py             # [未実装] 検証ロジック
```

## 重要なファイル

### `trace_schema.py`
Pydanticモデルでa2a-0.1スキーマを定義：
- `TraceJSON`: ルートスキーマ
- `Session`, `Model`, `Event`, `Usage`: サブスキーマ
- `Hashing`: Merkle Root情報

### `trace_builder.py`
LangChainの `agent.invoke()` 結果からTraceJSONを構築：
- `TraceBuilder.add_message()`: メッセージをイベント化
- `TraceBuilder.build()`: 最終的なTraceJSONを生成
- 自動的にMerkle Root計算を実行

### `merkle.py`
Merkle Root計算：
- `chunk_data()`: JSONを固定サイズチャンクに分割
- `compute_merkle_root()`: チャンクハッシュからツリー構築
- SHA256ハッシュ使用

### `demo_haiku_trace.py`
デモアプリケーション：
- `haiku_agent` を実行
- 結果を `TraceBuilder` で変換
- `traces/session-*.json` に保存

## A2A スキーマ（a2a-0.1）

### 主要フィールド

```python
{
  "traceVersion": "a2a-0.1",
  "session": {
    "id": str,           # セッションID
    "createdAt": str,    # ISO8601タイムスタンプ
    "actors": [str]      # 参加者リスト
  },
  "model": {
    "name": str,         # モデル名（例: gpt-5-nano-2025-08-07）
    "provider": str      # プロバイダー（例: openai）
  },
  "events": [
    {
      "type": "human_message" | "ai_message" | "ai_tool_call" | "tool_result",
      "ts": str,         # ISO8601タイムスタンプ
      "content": str?,
      "tool": str?,
      "args": dict?,
      "tool_call_id": str?
    }
  ],
  "usage": [
    {
      "turn": int,
      "input_tokens": int,
      "output_tokens": int
    }
  ],
  "hashing": {
    "algorithm": "sha256",
    "chunk_size": 4096,
    "chunkMerkleRoot": str,  # 16進数
    "chunks": [str]          # チャンクハッシュのリスト
  },
  "signatures": [...],       # 署名情報（未実装）
  "redactions": {...}        # マスキング情報（未実装）
}
```

## Merkle Root計算の詳細

1. **チャンク化**: TraceJSONを4096バイトのチャンクに分割
2. **ハッシュ化**: 各チャンクをSHA256でハッシュ
3. **ツリー構築**:
   - チャンクハッシュをリーフノードとする
   - ペアを連結してハッシュし、次のレベルを構築
   - 奇数個の場合は最後のノードをそのまま昇格
4. **Root取得**: 最終的に1つのハッシュ（Merkle Root）が残る

## 開発履歴

### 完了したタスク
1. ✅ プロジェクト構造作成
2. ✅ `trace_schema.py`: Pydanticスキーマ定義
3. ✅ `merkle.py`: Merkle Root計算
4. ✅ `trace_builder.py`: LangChain統合
5. ✅ `demo_haiku_trace.py`: デモ実装
6. ✅ `README.md`: ユーザー向けドキュメント
7. ✅ `claude.md`: 技術ドキュメント

### 次のタスク（Phase 2）

#### IPFS統合
```python
# a2a_anchor/ipfs_client.py

import ipfshttpclient

class IPFSClient:
    def __init__(self, api='/ip4/127.0.0.1/tcp/5001/http'):
        self.client = ipfshttpclient.connect(api)

    def add_json(self, trace_json: str) -> str:
        """Upload trace JSON to IPFS and return CID"""
        result = self.client.add_json(trace_json)
        return result  # CID

    def get_json(self, cid: str) -> str:
        """Retrieve JSON from IPFS by CID"""
        return self.client.get_json(cid)
```

#### XRPL統合
```python
# a2a_anchor/xrpl_client.py

from xrpl.wallet import Wallet
from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import Payment
from xrpl.transaction import submit_and_wait

class XRPLClient:
    def __init__(self, node_url: str, seed: str):
        self.client = JsonRpcClient(node_url)
        self.wallet = Wallet.from_seed(seed)

    def anchor_memo(self, cid: str, merkle_root: str, metadata: dict) -> str:
        """
        Record trace metadata to XRPL Memo
        Returns: transaction hash
        """
        memo_data = {
            "v": "a2a-0.1",
            "cid": cid,
            "root": merkle_root,
            **metadata
        }
        # Payment to self with Memo
        tx = Payment(
            account=self.wallet.classic_address,
            destination=self.wallet.classic_address,
            amount="1",  # 1 drop
            memos=[{"memo_data": json.dumps(memo_data).encode().hex()}]
        )
        result = submit_and_wait(tx, self.client, self.wallet)
        return result.result["hash"]
```

### 次のタスク（Phase 3）

#### 統合サービス
```python
# a2a_anchor/anchor_service.py

class AnchorService:
    def __init__(self, ipfs_client, xrpl_client):
        self.ipfs = ipfs_client
        self.xrpl = xrpl_client

    def anchor_trace(self, trace: TraceJSON) -> dict:
        """完全なアンカリングフロー"""
        # 1. IPFS保存
        trace_json = trace.to_json()
        cid = self.ipfs.add_json(trace_json)

        # 2. XRPL記録
        tx_hash = self.xrpl.anchor_memo(
            cid=cid,
            merkle_root=trace.hashing.chunkMerkleRoot,
            metadata={
                "sid": trace.session.id,
                "ts": int(datetime.now().timestamp()),
                "model": trace.model.name
            }
        )

        return {"cid": cid, "tx_hash": tx_hash}
```

#### 検証
```python
# a2a_anchor/verify.py

def verify_trace(tx_hash: str, xrpl_client, ipfs_client) -> bool:
    """トレースの完全性を検証"""
    # 1. XRPL Memoを取得
    memo = xrpl_client.get_memo(tx_hash)

    # 2. IPFSからJSON取得
    trace_json = ipfs_client.get_json(memo["cid"])

    # 3. Merkle Root再計算
    merkle_root, _ = compute_trace_merkle(trace_json)

    # 4. 一致確認
    return merkle_root == memo["root"]
```

## 設定管理

`.env` ファイル（現在のもの）:
```
OPENAI_API_KEY=...
LANGCHAIN_TRACING=true
LANGSMITH_API_KEY=...
```

将来追加する設定（Phase 2/3）:
```
# IPFS
IPFS_API=/ip4/127.0.0.1/tcp/5001/http

# XRPL Testnet
XRPL_NODE_URL=https://s.altnet.rippletest.net:51234
XRPL_SEED=s████████████
XRPL_ACCOUNT=r████████████
```

## テスト戦略

### 実装すべきテスト

```python
# tests/test_trace.py
def test_trace_builder_from_langchain():
    """LangChain結果からTraceJSONを構築"""

# tests/test_merkle.py
def test_merkle_root_calculation():
    """Merkle Root計算の正確性"""

def test_merkle_single_chunk():
    """単一チャンクの特殊ケース"""

# tests/test_ipfs.py (Phase 2)
def test_ipfs_upload_download():
    """IPFS保存・取得の往復テスト"""

# tests/test_xrpl.py (Phase 3)
def test_xrpl_memo_writing():
    """XRPL Testnetへの書き込み"""

def test_end_to_end_verification():
    """完全な検証フロー"""
```

## トラブルシューティング

### よくある問題

1. **Pydanticバージョン**: Pydantic v2が必要（`model_dump_json()`使用）
2. **IPFS接続**: ローカルIPFSノードが起動しているか確認
3. **XRPL Testnet**: ファウセットでテスト用XRPを取得する必要あり
4. **Memo容量制限**: XRPL Memoは1KBまで。超える場合はCIDとRootのみ記録

## 参考リンク

- [A2A Protocol Spec](https://github.com/anthropics/anthropic-tools/tree/main/schemas/a2a)
- [XRPL Memo Format](https://xrpl.org/transaction-common-fields.html#memos-field)
- [IPFS HTTP API](https://docs.ipfs.tech/reference/kubo/rpc/)
- [LangChain Agents](https://python.langchain.com/docs/modules/agents/)

## 開発時の注意点

1. **セキュリティ**: `.env`ファイルはgitignoreに含める（既に設定済み）
2. **PII対策**: 将来的にredaction機能を実装する（ユーザー情報のマスキング）
3. **スケーラビリティ**: 大規模トレースの場合、チャンクサイズの調整が必要
4. **コスト**: XRPL書き込みは1 dropで済むが、頻繁な書き込みは避ける

## 次に実装する機能の優先順位

1. **Phase 2a**: IPFS統合（`ipfs_client.py`）
2. **Phase 2b**: IPFSテスト（`tests/test_ipfs.py`）
3. **Phase 3a**: XRPL統合（`xrpl_client.py`）
4. **Phase 3b**: 統合サービス（`anchor_service.py`）
5. **Phase 3c**: 検証機能（`verify.py`）
6. **Phase 3d**: CLIツール（`cli.py`）

## コミット履歴

- `3783d35`: Initial commit
- （現在）: Phase 1完了 - トレース生成とMerkle Root計算
