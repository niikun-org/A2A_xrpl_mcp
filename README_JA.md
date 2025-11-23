# A2A Trace Anchoring on XRPL

**AIエージェントの全行動を、改ざん不可能な形で記録・検証できるオープンソースシステム**

**Tamper-proof recording and verification for every AI agent action**

📖 **[English Version / 英語版はこちら](README.md)**

## 🆕 新機能: MCP (Model Context Protocol) 統合！

このプロジェクトは**リアルタイムMCPツール呼び出しロギング**をGradio UIで提供します！

- 🔧 **5つのビルトインMCPツール**: 計算機、時計、文字数カウント、文字列反転、回文チェック
- 📊 **リアルタイム統計**: チャット中のツール使用状況を追跡
- 🔐 **完全なA2Aアンカリング**: すべてのMCPツール呼び出し → IPFS → XRPL with Merkle Root検証
- 🌐 **インタラクティブUI**: AIとチャットして透明なツールロギングを実際に体験

👉 **[クイックスタートガイド](QUICK_START.md)** | **[MCP統合の詳細](MCP_A2A_Trace_Logger_README.md)**

### ⚠️ 前提条件

**完全なアンカリング機能（IPFS + XRPL）にはDockerが必要です**:

```bash
# 1. Dockerをインストール（未インストールの場合）
#    Mac/Windows: https://www.docker.com/products/docker-desktop/
#    Linux: curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh

# 2. IPFSコンテナを起動
docker run -d --name ipfs -p 5001:5001 -p 8080:8080 ipfs/kubo

# 3. 依存関係をインストール
pip install -r requirements-mcp.txt

# 4. 今すぐ試す！
./run_mcp_demo.sh
# その後 http://localhost:7860 を開く
```

📖 **詳細なセットアップ手順は [QUICK_START.md](QUICK_START.md) を参照してください**

---

## プレゼンテーション

- サービスイメージは以下を参照してください。

https://niikun.net/A2A_demo.html


## 何ができるか

このプロジェクトは、LangChainエージェント（haiku_agent）の実行トレースを：

1. **標準化**: A2A形式（a2a-0.1）のJSON形式で記録
2. **完全性保証**: Merkle Rootによるハッシュ検証
3. **分散保存**: IPFS（分散ファイルシステム）に保存
4. **ブロックチェーン記録**: XRPL台帳に記録して改ざん検証可能

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

### ✅ Phase 4 完了（MCP統合！）
- 🆕 5つのツールを持つMCP (Model Context Protocol) サーバー
- 🆕 リアルタイムMCPツール呼び出しロギング
- 🆕 GradioベースのインタラクティブUI
- 🆕 ハイブリッドJSON-RPC + A2Aトレース形式
- 🆕 セッションベースのアンカリングワークフロー
- 🆕 リアルタイム統計とツール使用状況追跡

## デモの実行方法

### 🌐 NEW: MCPインタラクティブデモ（推奨！）

新しい**MCP対応インタラクティブデモ**をGradio UIで試してみましょう：

```bash
./run_mcp_demo.sh
# http://localhost:7860 を開く
```

**機能:**
- 💬 実際のツールを使用するAIとチャット（MCP経由）
- 📊 リアルタイムのツール使用統計を確認
- 🔐 完全なセッションをIPFS + XRPLにアンカリング
- 🔍 ブロックチェーン上で改ざん防止ログを検証

📖 **[完全なMCPセットアップガイド](QUICK_START.md)**

---

### 🌐 静的Webデモ

ブラウザで以下のHTMLファイルを開いてください：

#### 1. システム全体の動きを見る
```bash
open demo_interactive.html
```
**[demo_interactive.html](demo_interactive.html)** - アニメーション付きの解説デモ
- 🎬 7ステップアニメーション（MCP統合を含む！）
- ▶️ 自動再生機能
- ⌨️ キーボード操作（矢印キー、スペースキー）
- 📊 リアルタイムの進捗バー

#### 2. 実際のトレースファイルを見る
```bash
open trace_viewer.html
```
**[trace_viewer.html](trace_viewer.html)** - トレースファイルの可視化ツール
- 📁 ドラッグ&ドロップでJSONファイルを読み込み
- 📊 統計情報の表示
- ⏱️ イベントタイムライン
- 🔐 Merkle Root検証情報

---

### 🎓 ターミナルでの対話型デモ

```bash
uv run demo_simple_explanation.py
```

**このデモは、A2Aトレースアンカリングの仕組みを対話的に説明します。**
- ✨ ステップバイステップで仕組みを理解
- 📊 ビジュアルな図解
- 💡 実際の使用例
- 🔍 各フェーズの詳細説明

📖 **詳細な図解ドキュメント**: [EXPLANATION.md](./EXPLANATION.md)

---

### Phase 1: ローカル保存のみ

```bash
uv run demo_haiku_trace.py
```

### Phase 2: IPFS統合デモ

#### 1. IPFSノードを起動

```bash
# 新規起動
docker run -d --name ipfs -p 5001:5001 -p 8080:8080 ipfs/kubo
```

**注意:** すでにIPFSコンテナが存在する場合のトラブルシューティング：

```bash
# コンテナの状態を確認
docker ps -a | grep ipfs

# 停止している場合は再起動



# エラーが出る場合は削除して再作成
docker rm -f ipfs
docker run -d --name ipfs -p 5001:5001 -p 8080:8080 ipfs/kubo
```

#### 2. デモを実行

```bash
uv run demo_haiku_ipfs.py
```

### Phase 3: 完全なアンカリング（IPFS + XRPL）

#### 1. IPFSノードを起動

```bash
# コンテナの状態を確認
docker ps -a | grep ipfs

# 停止している場合は再起動
docker start ipfs

# 存在しない場合は新規作成
docker run -d --name ipfs -p 5001:5001 -p 8080:8080 ipfs/kubo
```

**注意:** Phase 2で既にIPFSを起動している場合、そのまま使えます。

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

#### Phase 3（完全なアンカリング）

Phase 1, 2の出力に加えて：

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

### 4. トレースの検証

#### ローカルファイルを確認

```bash
cat traces/session-*.json | jq .
```

#### IPFSから取得して検証

```bash
# Pythonで検証（推奨）
uv run python -c "from a2a_anchor.ipfs_client import create_ipfs_client; client = create_ipfs_client(); trace = client.get_json('<CID>'); print(f\"Session: {trace['session']['id']}\"); print(f\"Merkle Root: {trace['hashing']['chunkMerkleRoot']}\")"

# または、IPFSゲートウェイ経由（ポート8080が公開されている場合）
curl http://127.0.0.1:8080/ipfs/<CID> | jq .

# 公開IPFSゲートウェイを使う場合
curl https://ipfs.io/ipfs/<CID> | jq .
```

**注意:** GitHub Codespacesを使用している場合：
1. VSCodeの「ポート」タブを開く
2. ポート8080を見つけて「公開範囲」を「Public」に変更
3. または、Pythonから直接IPFSにアクセス（上記のコマンド）

#### XRPLトランザクションから完全検証

```bash
# トランザクションハッシュから検証（実際の例）
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

# 実際のトランザクション例
tx_hash = '8313F6124E4FEAEB545932DED7FB46CFD2E85203ED6756C9EE58B4943F01AA21'
result = verifier.verify(tx_hash)

print(f'Verified: {result.verified}')
print(f'Session ID: {result.session_id}')
print(f'IPFS CID: {result.cid}')
print(f'Merkle Root Match: {result.expected_root == result.computed_root}')
"
```

## 実際の検証例

以下は、実際にXRPL Testnetに記録されたトレースの検証例です：

### 検証可能なトランザクション

**トランザクションハッシュ**: `8313F6124E4FEAEB545932DED7FB46CFD2E85203ED6756C9EE58B4943F01AA21`

- **XRPL Explorer**: https://testnet.xrpl.org/transactions/8313F6124E4FEAEB545932DED7FB46CFD2E85203ED6756C9EE58B4943F01AA21
- **Ledger Index**: 12180011
- **Session ID**: session-c6258f2777c2
- **IPFS CID**: QmSYKU3iV1u53RP2jCbQV9coDJRLJYoiNJTdLyDUTYGGHT
- **Merkle Root**: e5d295ed807b7881eb2e2e977a04e9922c991f736dbe80a059846aa5e1aef673
- **Model**: gpt-5-nano-2025-08-07
- **Events**: 8個（AIエージェントとツールのやり取り）

### このトランザクションを検証する

```bash
# 1. IPFSからトレースデータを取得
curl http://127.0.0.1:8080/ipfs/QmSYKU3iV1u53RP2jCbQV9coDJRLJYoiNJTdLyDUTYGGHT | jq .

# 2. Pythonで完全な検証を実行
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
├── mcp/                     # 🆕 MCP統合
│   ├── app.py               # MCPデモ用Gradio UI
│   ├── mcp_server.py        # 5つのツールを持つMCPサーバー
│   ├── mcp_client.py        # MCPクライアント実装
│   ├── logger.py            # ハイブリッドJSON-RPCロガー
│   └── mcp_trace_builder.py # MCP → A2Aトレース変換
├── tests/                   # テストコード
│   ├── test_ipfs.py         # IPFSクライアントのテスト
│   └── test_xrpl.py         # XRPLクライアントのテスト
├── demo_haiku_trace.py      # デモ：Phase 1（ローカル保存）
├── demo_haiku_ipfs.py       # デモ：Phase 2（IPFS統合）
├── demo_full_anchor.py      # デモ：Phase 3（完全なアンカリング）
├── test_mcp_basic.py        # 🆕 MCP統合テスト
├── run_mcp_demo.sh          # 🆕 MCPデモ起動スクリプト
├── haiku_agent.py           # Haikuを生成するLangChainエージェント
├── logs/                    # 🆕 MCPセッションログ（JSON-RPC）
├── traces/                  # 生成されたA2Aトレースファイル
├── QUICK_START.md           # 🆕 MCPデモのクイックスタート
└── a2a_xrpl_spec.md        # 仕様書
```

## 記録される情報

### 従来のA2Aトレース
- **ユーザーメッセージ**: エージェントへの入力
- **AIメッセージ**: エージェントの応答
- **ツール呼び出し**: check_haiku_lines等のツール実行
- **ツール結果**: ツールの実行結果
- **メタデータ**: モデル名、トークン使用量、タイムスタンプ
- **完全性検証**: Merkle Root（改ざん検知用）

### 🆕 MCPハイブリッドログ
- **JSON-RPCリクエスト**: 完全なMCPツール呼び出し詳細
- **JSON-RPCレスポンス**: 完全なツール実行結果
- **セッションメタデータ**: セッションID、タイムスタンプ、アクター情報
- **ツール統計**: ツール使用回数、成功/失敗率
- **レイテンシ追跡**: 各ツール呼び出しの応答時間
- **A2A変換**: ハイブリッドログをA2A形式に変換してアンカリング

## なぜこれが必要か

### 問題
- LLMエージェントの実行ログは改ざんされる可能性がある
- 誰がどのツールを何回実行したか、証明できない
- 監査やコンプライアンスのために実行履歴の証明が必要

### 解決策（✅ 実装済み）
1. **標準化**: A2A形式で誰でも読める形式に記録
2. **ハッシュ化**: Merkle Rootで内容の完全性を保証
3. **分散保存**: IPFSで永続的かつ分散的に保存
4. **ブロックチェーン記録**: XRPL TestnetにCID+Merkle Rootを記録
5. **完全な検証**: トランザクションハッシュから元のトレースまで検証可能

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

### Phase 4: MCP統合
- ✅ 5つのツールを持つMCPサーバー（calculator, clock, word_count, reverse_string, check_palindrome）
- ✅ MCPクライアント実装
- ✅ ハイブリッドJSON-RPCロギングシステム
- ✅ GradioベースのインタラクティブUI
- ✅ リアルタイムツール使用統計
- ✅ セッションベースのログアンカリング
- ✅ MCP → A2Aトレース変換
- ✅ ワンクリックでIPFS + XRPLにアンカリング

## アーキテクチャ

### 従来のLangChainフロー
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

### 🆕 MCP統合フロー
```
1. ユーザーチャット（Gradio UI）
   ↓
2. LLMがMCPクライアント経由でMCPツールを呼び出し
   ↓
3. Logger: JSON-RPCリクエスト/レスポンスをキャプチャ
   ↓
4. logs/events.jsonl: ハイブリッドログ（JSON-RPC + A2Aメタデータ）
   ↓
5. ユーザーが"Anchor Session Logs"ボタンをクリック
   ↓
6. MCP Trace Builder: A2A形式に変換
   ↓
7. Merkle Root計算
   ↓
8. IPFSアップロード → CID取得
   ↓
9. XRPLアンカリング → TX Hash取得
   ↓
10. TX Hashから検証可能
```

## ⚠️ 現在の制約とセキュリティ上の注意

### 未実装機能

⚠️ **署名機能は未実装です**
- トレースには作成者を証明する暗号署名が含まれていません
- システムにアクセスできる人は誰でもトレースを作成できます
- JSON内の`"signatures": []`フィールドは現在空です

⚠️ **PIIマスキングは未実装です**
- **本番データや機密データでは追加の保護措置なしに使用しないでください**
- 個人情報、APIキー、パスワードはそのままログに記録されます
- `"redactions"`フィールドは存在しますが、自動マスキングは行われません
- **推奨**: テストデータのみを使用するか、入力を手動でサニタイズしてください

### セキュリティのベストプラクティス

#### 🔐 環境変数（.env）の管理

**絶対に`.env`をバージョン管理にコミットしないでください！**

```bash
# .gitignoreに以下を含める:
.env
*.env
.env.*
```

**XRPL_SEEDの安全な保管:**
```bash
# 制限的なパーミッションを使用
chmod 600 .env

# 本番環境では以下を使用:
# - ハードウェアセキュリティモジュール（HSM）
# - クラウドシークレットマネージャー（AWS Secrets Manager、GCP Secret Manager）
# - 環境専用のVault（HashiCorp Vault）
```

**TestnetとMainnetの使い分け:**
- ✅ このプロジェクトはデフォルトでXRPL **Testnet**を使用（テストXRP、実際の価値なし）
- ⚠️ 開発/デモ環境で**Mainnetのシードを使用しないでください**
- 🔒 Testnetフォーセット: https://xrpl.org/xrp-testnet-faucet.html

#### 🌐 Gradio UIのセキュリティ

⚠️ **Gradio UIはローカル使用のみを想定しています**

**以下なしに公開しないでください:**
1. **認証**（最低限ベーシック認証）
2. **HTTPS/TLS暗号化**
3. **レート制限**（悪用防止）
4. **入力検証**とサニタイゼーション

**公開デプロイメントの場合:**
```python
# mcp/app.pyに認証を追加
demo.launch(
    auth=("username", "password"),  # ベーシック認証を追加
    ssl_certfile="cert.pem",        # HTTPSを有効化
    ssl_keyfile="key.pem"
)
```

### ログ・トレースファイルの運用管理

#### ディスク容量管理

ログとトレースは時間とともに蓄積されます：

```bash
# 現在の使用量を確認
du -sh logs/ traces/

# ログをローテーション（過去30日分を保持）
find logs/ -name "*.jsonl" -mtime +30 -delete

# 古いトレースをアーカイブ
tar -czf traces_archive_$(date +%Y%m%d).tar.gz traces/
find traces/ -name "*.json" -mtime +90 -delete
```

#### 自動クリーンアップ（Cronジョブの例）

```bash
# crontabに追加（crontab -e）
# 毎日午前2時に実行
0 2 * * * find /path/to/logs -name "*.jsonl" -mtime +30 -delete
0 2 * * * find /path/to/traces -name "*.json" -mtime +90 -delete
```

#### ログ保持期間の推奨

| ファイル種別 | 場所 | 保持期間 | 備考 |
|-------------|------|---------|------|
| MCPセッションログ | `logs/events.jsonl` | 30日 | すべてのツール呼び出しを含む |
| A2Aトレース | `traces/*.json` | 90日 | アンカー済みトレース（IPFSから取得可能） |
| IPFSピン済みコンテンツ | IPFSノード | 永続 | 手動でアンピンするまで |
| XRPLトランザクション | XRPLレジャー | 永続 | 不変のブロックチェーン記録 |

#### プライバシーに関する考慮事項

**IPFS/XRPLにアンカリングする前に:**
- ✅ トレース内容に機密情報がないか確認してください
- ✅ 重要: IPFSとXRPLは**公開されており永続的**です
- ✅ 一度アンカリングすると、データはブロックチェーンから**削除できません**
- ⚠️ 公開しても問題ないデータのみを使用してください

---

## 将来の拡張

以下の機能は計画されていますが、まだ実装されていません：

- **署名機能（EIP-191-like）**: トレースの真正性と作成者を証明するデジタル署名
- **Redaction（PIIマスキング）**: 個人情報の自動検出とマスキング、GDPR対応
- XRPL EVM サイドチェーンでのEAS互換化
- ZK証明による内容非公開検証
- Next.jsビューアでの時系列表示
- CLIツール（`a2a` コマンド）

## 参考

- 詳細仕様: [a2a_xrpl_spec.md](./a2a_xrpl_spec.md)
- XRPL: https://xrpl.org/
- IPFS: https://ipfs.tech/

## License

Copyright 2025 niikun

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

