# A2A Trace Anchoring on XRPL

LLMエージェントの実行ログを **改ざん検証可能** な形で記録するシステムのデモ実装です。

## 何ができるか

このプロジェクトは、LangChainエージェント（haiku_agent）の実行トレースを：

1. **標準化**: A2A形式（a2a-0.1）のJSON形式で記録
2. **完全性保証**: Merkle Rootによるハッシュ検証
3. **将来的に**: IPFS + XRPL台帳に記録して改ざん検証

## 現在の実装状況

### ✅ Phase 1 完了
- LangChainエージェントの実行ログをA2A形式に変換
- Merkle Root計算による完全性検証
- JSONファイルとしてローカル保存

### ✅ Phase 2 完了
- IPFS統合（トレースをIPFSに保存、CID取得）
- IPFS検証機能（CIDからトレース取得、Merkle Root検証）

### ✅ Phase 3 完了（全機能実装完了！）
- XRPL統合（Testnetへのアンカリング、Memo記録）
- 完全な検証フロー（XRPL → IPFS → Merkle Root検証）
- 統合サービス（AnchorService）による一括処理
- エンドツーエンドの検証システム

## デモの実行方法

### Phase 1: ローカル保存のみ

```bash
uv run demo_haiku_trace.py
```

### Phase 2: IPFS統合デモ

#### 1. IPFSノードを起動

```bash
docker run -d --name ipfs -p 5001:5001 -p 8080:8080 ipfs/kubo
```

#### 2. デモを実行

```bash
uv run demo_haiku_ipfs.py
```

### Phase 3: 完全なアンカリング（IPFS + XRPL）

#### 1. IPFSノードを起動

```bash
docker run -d --name ipfs -p 5001:5001 -p 8080:8080 ipfs/kubo
```

#### 2. XRPL Testnetアカウントを取得

1. [XRPL Testnet Faucet](https://xrpl.org/xrp-testnet-faucet.html)にアクセス
2. "Generate"をクリックしてTestnetアカウントを作成
3. 表示された`Secret`（seed）を`.env`ファイルに追加：

```bash
XRPL_SEED=sXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

#### 3. デモを実行

```bash
uv run demo_full_anchor.py
```

### 3. 実行結果

#### Phase 1（ローカル保存のみ）

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

#### Phase 2（IPFS統合）

Phase 1の出力に加えて：

```
=== Phase 2: Uploading to IPFS ===
Connected to IPFS node (version: 0.x.x)
✓ Trace uploaded to IPFS
  CID: bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi
  IPFS URL: ipfs://bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi
  Gateway URL: http://localhost:8080/ipfs/bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi
✓ Content pinned to prevent garbage collection

=== Verifying IPFS retrieval ===
✓ Merkle Root verification: PASSED
  Expected: 43b10e78082bfd87c859ca55766d4abfebda42e5686c63509754b641ed93a9f5
  Retrieved: 43b10e78082bfd87c859ca55766d4abfebda42e5686c63509754b641ed93a9f5

=== Phase 2 Complete ===
Local file: traces/session-XXXXX.json
IPFS CID: bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi
```

#### Phase 3（完全なアンカリング）

Phase 1, 2の出力に加えて：

```
=== Step 5: Anchoring to IPFS + XRPL ===
Uploading to IPFS...
Anchoring to XRPL Testnet...

✓ Anchoring Complete!
  Session ID: session-XXXXX
  IPFS CID: bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi
  XRPL TX Hash: 1A2B3C4D5E6F...
  Ledger Index: 12345678
  Merkle Root: 43b10e78082bfd87c859ca55766d4abfebda42e5686c63509754b641ed93a9f5

=== Step 6: Verifying Anchored Trace ===
1. Retrieving memo from XRPL...
2. Fetching trace from IPFS...
3. Recalculating Merkle Root...
4. Comparing with anchored root...

✓ VERIFICATION PASSED
  Expected Root: 43b10e78082bfd87c859ca55766d4abfebda42e5686c63509754b641ed93a9f5
  Computed Root: 43b10e78082bfd87c859ca55766d4abfebda42e5686c63509754b641ed93a9f5
  Match: ✓ YES

Explore on XRPL:
  https://testnet.xrpl.org/transactions/1A2B3C4D5E6F...
```

### 4. トレースの検証

#### ローカルファイルを確認

```bash
cat traces/session-*.json | jq .
```

#### IPFSから取得して検証

```bash
# CIDを使ってトレースを取得
curl http://localhost:8080/ipfs/<CID> | jq .

# Pythonで検証
uv run python -c "from a2a_anchor.ipfs_client import create_ipfs_client; client = create_ipfs_client(); trace = client.get_json('<CID>'); print(f\"Session: {trace['session']['id']}\"); print(f\"Merkle Root: {trace['hashing']['chunkMerkleRoot']}\")"
```

#### XRPLトランザクションから完全検証

```bash
# トランザクションハッシュから検証
uv run python -c "
from a2a_anchor.xrpl_client import create_xrpl_client
from a2a_anchor.ipfs_client import create_ipfs_client
from a2a_anchor.verify import verify_trace
import os

xrpl = create_xrpl_client(
    os.getenv('XRPL_NODE_URL'),
    seed=os.getenv('XRPL_SEED'),
    network='testnet'
)
ipfs = create_ipfs_client()
result = verify_trace('<TX_HASH>', xrpl, ipfs)
print(result)
"
```

## トレースファイルの内容

生成されるJSONには以下が含まれます：

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

## プロジェクト構成

```
.
├── a2a_anchor/              # A2Aアンカリングライブラリ
│   ├── __init__.py
│   ├── trace_schema.py      # A2A JSONスキーマ定義（Pydantic）
│   ├── trace_builder.py     # LangChain結果→A2A変換
│   ├── merkle.py            # Merkle Root計算
│   ├── ipfs_client.py       # IPFS統合（Phase 2）
│   ├── xrpl_client.py       # XRPL統合（Phase 3）
│   ├── anchor_service.py    # 統合アンカリングサービス（Phase 3）
│   └── verify.py            # 検証モジュール（Phase 3）
├── tests/                   # テストコード
│   ├── test_ipfs.py         # IPFSクライアントのテスト
│   └── test_xrpl.py         # XRPLクライアントのテスト
├── demo_haiku_trace.py      # デモ：Phase 1（ローカル保存）
├── demo_haiku_ipfs.py       # デモ：Phase 2（IPFS統合）
├── demo_full_anchor.py      # デモ：Phase 3（完全なアンカリング）
├── haiku_agent.py           # Haikuを生成するLangChainエージェント
├── traces/                  # 生成されたトレースファイル
└── a2a_xrpl_spec.md        # 仕様書
```

## 記録される情報

- **ユーザーメッセージ**: エージェントへの入力
- **AIメッセージ**: エージェントの応答
- **ツール呼び出し**: check_haiku_lines等のツール実行
- **ツール結果**: ツールの実行結果
- **メタデータ**: モデル名、トークン使用量、タイムスタンプ
- **完全性検証**: Merkle Root（改ざん検知用）

## なぜこれが必要か

### 問題
- LLMエージェントの実行ログは改ざんされる可能性がある
- 誰がどのツールを何回実行したか、証明できない

### 解決策
1. **標準化**: A2A形式で誰でも読める形式に
2. **ハッシュ化**: Merkle Rootで内容の完全性を保証
3. **台帳記録**（未実装）: IPFS + XRPL でタイムスタンプと検証可能性

## テストの実行

### IPFSテスト

```bash
# IPFSノードを起動
docker run -d --name ipfs -p 5001:5001 -p 8080:8080 ipfs/kubo

# テストを実行
uv run pytest tests/test_ipfs.py -v

# IPFSがない場合はスキップ
uv run pytest -k "not ipfs"
```

### XRPLテスト

```bash
# .envファイルにXRPL_SEEDを設定

# テストを実行
uv run pytest tests/test_xrpl.py -v

# XRPLがない場合はスキップ
uv run pytest -k "not xrpl"
```

### 統合テスト

```bash
# IPFS + XRPL両方必要
uv run pytest tests/test_xrpl.py::test_full_integration_anchor_and_verify -v
```

## 実装された機能

### Phase 1: ローカルトレース記録
- ✅ LangChainエージェント実行ログの取得
- ✅ A2A形式（a2a-0.1）への変換
- ✅ Merkle Root計算
- ✅ JSONファイル保存

### Phase 2: IPFS統合
- ✅ IPFSクライアント実装
- ✅ トレースのIPFSアップロード
- ✅ CID取得とピン機能
- ✅ IPFSからの取得と検証

### Phase 3: XRPL統合
- ✅ XRPLクライアント実装
- ✅ XRPL Testnetへのトランザクション送信
- ✅ MemoフィールドへのCID + Merkle Root記録
- ✅ 統合アンカリングサービス（AnchorService）
- ✅ 完全な検証フロー（verify.py）
- ✅ エンドツーエンドテスト

## アーキテクチャ

```
1. LangChainエージェント実行
   ↓
2. TraceBuilder: messages → A2A JSON
   ↓
3. Merkle計算: JSON → チャンク化 → Merkle Root
   ↓
4. IPFS保存: JSON → CID取得 → Pin
   ↓
5. XRPL記録: Payment TX + Memo {cid, root, meta}
   ↓
6. 検証: TX Hash → Memo → CID → IPFS → JSON → Merkle Root再計算 → 比較
```

## 将来の拡張

以下の機能は仕様書に含まれていますが、現在のMVPでは未実装です：

- XRPL EVM サイドチェーンでのEAS互換化
- ZK証明による内容非公開検証
- Next.jsビューアでの時系列表示
- 署名機能（EIP-191-like）
- Redaction（PII masking）機能
- CLIツール（`a2a` コマンド）

## 参考

- 詳細仕様: [a2a_xrpl_spec.md](./a2a_xrpl_spec.md)
- XRPL: https://xrpl.org/
- IPFS: https://ipfs.tech/
