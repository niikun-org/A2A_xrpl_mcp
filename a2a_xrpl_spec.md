# A2A Trace Anchoring on XRPL — Python 実装仕様書（v0.9）

## 1. スコープ
- LLM/Agent とツールの **やりとり（トレース）** を JSON で標準化し、  
  1) IPFS に保存（大容量・低コスト）  
  2) XRPL の **Memo**（または XLS-20 NFT の URI）に **CID/Merkle Root** を記録  
- 第三者が **改ざん検証**（ハッシュ再計算＋台帳参照）できるようにする  
- MVP は **公開読み取り専用**、書き込みは運用者のみ。

---

## 2. 用語
| 用語 | 説明 |
|------|------|
| **Trace JSON** | A2A の逐次イベントログ（ユーザ/AI/ツール、モデル名、トークンなど） |
| **CID** | IPFS コンテンツID（コンテンツのハッシュ） |
| **Merkle Root** | JSON チャンク群のハッシュツリーの根 |
| **XRPL Memo** | トランザクションに付与できる 1KB までのメモ（Hexエンコード） |

---

## 3. アーキテクチャ
```
LangChain(任意)
   ↓
TraceBuilder(Python)
   ↓  (チャンク化+ハッシュ)
   ↓
IPFS保存 → CID取得
   ↓
XRPLトランザクション(Memoに {cid, root, meta})
   ↓
Viewer/Verifier(Python/Next.js) が検証・表示
```

---

## 4. データ仕様

### 4.1 Trace JSON フォーマット（a2a-0.1）
```json
{
  "traceVersion": "a2a-0.1",
  "session": {
    "id": "lc_run--b542f9...",
    "createdAt": "2025-11-02T19:41:00+09:00",
    "actors": ["user","assistant","tool:check_haiku_lines"]
  },
  "model": {
    "name": "openai:gpt-5-nano-2025-08-07",
    "provider": "openai"
  },
  "events": [
    {"type":"human_message","ts":"2025-11-02T19:41:02+09:00","content":"please write a poem."},
    {"type":"ai_tool_call","tool":"check_haiku_lines","args":{"text":"..."}, "tool_call_id":"call_..."},
    {"type":"tool_result","tool":"check_haiku_lines","content":"Correct!!"},
    {"type":"ai_message","content":"Field lamps cut the dusk\nPitcher winds..."}
  ],
  "usage": [
    {"turn":1,"input_tokens":171,"output_tokens":1391}
  ],
  "hashing": {
    "algorithm": "sha256",
    "chunk_size": 4096,
    "chunkMerkleRoot": null,
    "chunks": []
  },
  "signatures": [
    {"actor":"recorder","address":"rXXXXXXXXXXXXXXXXXXXX","spec":"EIP-191-like","signature":null}
  ],
  "redactions": {"policy":"pii_mask","masked_fields":[]}
}
```

---

### 4.2 XRPL Memo ペイロード仕様
```json
{
  "v":"a2a-0.1",
  "sid":"lc_run--b542f9...",
  "cid":"ipfs://bafybeigd...",
  "root":"0xabc123...",
  "ts":1730544060,
  "model":"gpt-5-nano-2025-08-07"
}
```

---

### 4.3 NFT（XLS-20）運用（任意）
- 1セッション=1NFTを mint
- URI に `ipfs://...`（CID）を記録
- 公開・アーカイブ用途に利用可能

---

## 5. Python 実装構成
```
a2a_anchor/
  ├── config.py
  ├── trace_schema.py
  ├── trace_builder.py
  ├── merkle.py
  ├── ipfs_client.py
  ├── xrpl_client.py
  ├── anchor_service.py
  ├── verify.py
  └── cli.py
tests/
  ├── test_trace.py
  ├── test_merkle.py
  ├── test_ipfs.py
  └── test_xrpl.py
```

---

## 6. 処理フロー
1. Trace 構築 → JSON化  
2. チャンク化 & Merkle root 計算  
3. IPFS に pin → CID 取得  
4. XRPL Memo へ書き込み  
5. tx_hash を控えて検証へ

---

## 7. 検証プロセス
1. 台帳から `tx_hash` → Memo を取得  
2. Memo の CID で IPFS から JSON 取得  
3. Merkle Root 再計算  
4. Memo 内 Root と一致すれば **OK**

---

## 8. CLI コマンド仕様
| コマンド | 内容 |
|-----------|------|
| `a2a init` | 設定ファイル生成 |
| `a2a build` | Trace正規化 |
| `a2a anchor` | IPFS pin + XRPL Memo登録 |
| `a2a verify` | トランザクションから検証 |

---

## 9. 設定ファイル
`~/.a2a-anchor/config.toml`
```toml
[xrpl]
node_url = "https://s.altnet.rippletest.net:51234"
seed = "s████████████"
account = "r████████████"

[ipfs]
api = "/ip4/127.0.0.1/tcp/5001/http"
```

---

## 10. エラー処理
- IPFS 失敗 → リトライ
- XRPL Fee 衝突 → 再送
- Memo 1KB 超過 → Root のみ記録にフォールバック

---

## 11. セキュリティ・プライバシー
- 機微情報は `[REDACTED]` でマスク
- 署名：XRPL アカウント署名で否認防止
- 改変検出：Merkle Root による完全性保証

---

## 12. 将来拡張
- XRPL EVM サイドチェーンで EAS 互換化
- ZK 証明による内容非公開検証
- Next.js ビューアで時系列表示

---

## 13. 受け入れ基準（MVP）
- `trace.json → CID → XRPL Memo` 一連処理が完了  
- `verify` コマンドが True を返す  
- Trace 改変で検証失敗が確認できる
