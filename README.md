# A2A Trace Anchoring on XRPL

LLMエージェントの実行ログを **改ざん検証可能** な形で記録するシステムのデモ実装です。

## 何ができるか

このプロジェクトは、LangChainエージェント（haiku_agent）の実行トレースを：

1. **標準化**: A2A形式（a2a-0.1）のJSON形式で記録
2. **完全性保証**: Merkle Rootによるハッシュ検証
3. **将来的に**: IPFS + XRPL台帳に記録して改ざん検証

## 現在の実装状況（Phase 1）

### ✅ 実装済み
- LangChainエージェントの実行ログをA2A形式に変換
- Merkle Root計算による完全性検証
- JSONファイルとしてローカル保存

### 🚧 未実装（Phase 2/3）
- IPFS統合（トレースをIPFSに保存、CID取得）
- XRPL統合（Testnetへのアンカリング、Memo記録）

## デモの実行方法

### 1. デモを実行

```bash
uv run demo_haiku_trace.py
```

### 2. 実行結果

以下が表示されます：

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

### 3. トレースファイルを確認

```bash
cat traces/session-*.json | jq .
```

または直接ファイルを開きます：`traces/session-XXXXX.json`

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
│   └── merkle.py            # Merkle Root計算
├── demo_haiku_trace.py      # デモ：haiku_agentのトレース記録
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

## 次のステップ

### Phase 2: IPFS統合
```bash
# Docker でIPFSノードを起動
docker run -d --name ipfs -p 5001:5001 ipfs/kubo

# トレースをIPFSに保存
a2a anchor --trace traces/session-*.json
# → CID取得
```

### Phase 3: XRPL統合
```bash
# XRPL TestnetにMemoとして記録
a2a anchor --trace traces/session-*.json --xrpl
# → tx_hash取得

# 検証
a2a verify --tx <tx_hash>
# → ハッシュ再計算 → 台帳と比較 → OK/NG
```

## 参考

- 詳細仕様: [a2a_xrpl_spec.md](./a2a_xrpl_spec.md)
- XRPL: https://xrpl.org/
- IPFS: https://ipfs.tech/
