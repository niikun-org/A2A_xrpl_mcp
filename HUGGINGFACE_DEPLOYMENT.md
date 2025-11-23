# 🚀 HuggingFace Spaces デプロイメントガイド

## 概要

このプロジェクトをHuggingFace Spacesにデプロイして、ブラウザから直接アクセスできるデモを公開できます。

## 🐳 2つのデプロイオプション

### オプション1: Gradio Space（制限あり・無料）

**特徴:**
- ✅ 無料で使用可能
- ✅ MCPツール呼び出しは動作
- ❌ IPFSは利用不可（Dockerなし）
- ❌ XRPLアンカリングは推奨しない（秘密鍵管理）

**推奨用途:** MCPツールのデモのみ

### オプション2: Docker Space（完全機能・有料）

**特徴:**
- ✅ IPFS完全サポート（Dockerコンテナ内）
- ✅ XRPLアンカリング対応（Secrets経由で秘密鍵管理）
- ✅ 完全な検証フロー
- ⚠️ 有料プラン必要（CPU upgrade: $9/月〜）

**推奨用途:** フル機能のデモ・本番環境

---

## 📊 機能比較表

| 機能 | ローカル | Gradio Space | Docker Space | 備考 |
|------|---------|--------------|--------------|------|
| MCPツール呼び出し | ✅ | ✅ | ✅ | Python環境で動作 |
| A2Aトレース生成 | ✅ | ✅ | ✅ | Python環境で動作 |
| リアルタイム統計 | ✅ | ✅ | ✅ | メモリ内処理 |
| IPFS アップロード | ✅ | ❌ | ✅ | Dockerが必要 |
| XRPL アンカリング | ✅ | △ | ✅ | 秘密鍵の管理が必要 |
| トレース検証 | ✅ | ❌ | ✅ | IPFSアクセスが必要 |
| 月額料金 | $0 | **$0** | **$9〜** | Docker = 有料プラン |

---

## 🎯 オプション1: Gradio Space（無料・制限あり）

### デプロイ手順

#### 方法1: Web UIからアップロード（推奨）

1. **HuggingFace アカウント作成**
   - https://huggingface.co/ にアクセス
   - アカウントを作成（無料）

2. **新しいSpaceを作成**
   - https://huggingface.co/new-space にアクセス
   - Space名を入力（例: `a2a-mcp-demo`）
   - License: `Apache 2.0`
   - SDK: `Gradio`
   - Hardware: `CPU basic`（無料）
   - Create Space をクリック

3. **ファイルをアップロード**

   必須ファイル:
   ```
   app.py                    # エントリーポイント
   requirements.txt          # 依存関係
   README_SPACES.md          # Spaces用README
   .spacesconfig.yaml        # Space設定（オプション）
   ```

   プロジェクトファイル:
   ```
   mcp/                      # MCPモジュール全体
   ├── app.py
   ├── mcp_server.py
   ├── mcp_client.py
   ├── logger.py
   └── mcp_trace_builder.py

   a2a_anchor/              # A2Aライブラリ全体
   ├── __init__.py
   ├── trace_schema.py
   ├── trace_builder.py
   ├── merkle.py
   ├── ipfs_client.py
   ├── xrpl_client.py
   ├── anchor_service.py
   └── verify.py
   ```

4. **README設定**
   - Spaces UIで `README_SPACES.md` の内容を `README.md` にコピー
   - または `README_SPACES.md` をそのまま使用

5. **デプロイ**
   - ファイルアップロード後、自動的にビルドが開始
   - ログを確認してエラーがないか確認
   - ビルド完了後、Spaceが公開される

#### 方法2: Git経由でデプロイ

```bash
# 1. HuggingFaceにログイン
huggingface-cli login

# 2. Spaceをクローン（Space名は事前にWeb UIで作成）
git clone https://huggingface.co/spaces/YOUR_USERNAME/a2a-mcp-demo
cd a2a-mcp-demo

# 3. 必要なファイルをコピー
cp /path/to/A2A_xrpl_mcp/app.py .
cp /path/to/A2A_xrpl_mcp/requirements.txt .
cp /path/to/A2A_xrpl_mcp/README_SPACES.md README.md
cp /path/to/A2A_xrpl_mcp/.spacesconfig.yaml .
cp -r /path/to/A2A_xrpl_mcp/mcp .
cp -r /path/to/A2A_xrpl_mcp/a2a_anchor .

# 4. コミットしてプッシュ
git add .
git commit -m "Initial deployment"
git push

# 5. Spaceが自動的にビルド・デプロイされる
```

---

## 🐳 オプション2: Docker Space（完全機能・有料）

### 前提条件

- HuggingFace Pro アカウント（$9/月〜）
- または CPU upgrade hardware ($9/月〜)

### デプロイ手順

#### 1. Spaceを作成

Web UIから:
- https://huggingface.co/new-space にアクセス
- Space名を入力（例: `a2a-mcp-full`）
- License: `Apache 2.0`
- **SDK: `Docker`** ← 重要！
- Hardware: `CPU upgrade` 以上
- Create Space をクリック

#### 2. 必要なファイル

Docker Spaceでは以下のファイルが必要:

```
Dockerfile                 # Docker設定（IPFS含む）
requirements.txt           # Python依存関係
README_SPACES.md          # 説明文
.spacesconfig-docker.yaml # Docker Space設定
mcp/                      # MCPモジュール全体
a2a_anchor/              # A2Aライブラリ全体
app.py                   # エントリーポイント
```

#### 3. Git経由でデプロイ

```bash
# 1. Spaceをクローン
git clone https://huggingface.co/spaces/YOUR_USERNAME/a2a-mcp-full
cd a2a-mcp-full

# 2. すべてのファイルをコピー
cp /path/to/A2A_xrpl_mcp/Dockerfile .
cp /path/to/A2A_xrpl_mcp/requirements.txt .
cp /path/to/A2A_xrpl_mcp/README_SPACES.md README.md
cp /path/to/A2A_xrpl_mcp/.spacesconfig-docker.yaml .spacesconfig.yaml
cp /path/to/A2A_xrpl_mcp/app.py .
cp -r /path/to/A2A_xrpl_mcp/mcp .
cp -r /path/to/A2A_xrpl_mcp/a2a_anchor .

# 3. コミットしてプッシュ
git add .
git commit -m "Docker deployment with IPFS support"
git push
```

#### 4. Secretsの設定

HuggingFace Spaces UI → Settings → Repository secrets:

```
XRPL_SEED=sXXXXXXXXXXXXXXXXXXXXXXX
```

**取得方法:**
1. https://xrpl.org/xrp-testnet-faucet.html にアクセス
2. "Generate Faucet Credentials" をクリック
3. 表示された `Secret` をコピー
4. Spaces Secrets に `XRPL_SEED` として追加

⚠️ **重要:** Testnetのシードのみを使用！Mainnetは使用しないでください。

#### 5. ビルドとデプロイ

- Pushすると自動的にDockerイメージがビルドされます
- ビルドには5-10分かかる場合があります
- ログでIPFSの起動を確認:
  ```
  📦 Starting IPFS daemon...
  ✅ IPFS is ready
  📡 Starting MCP server...
  🌐 Starting Gradio UI...
  ```

### Dockerfileの説明

作成された `Dockerfile` は以下を実行します:

1. **Python 3.10環境** をベースに構築
2. **IPFS (Kubo)** をインストール
3. IPFSを**ローカル専用**に設定（セキュリティ）
4. Python依存関係をインストール
5. **起動スクリプト** で以下を順次起動:
   - IPFS daemon (バックグラウンド)
   - MCP server (バックグラウンド)
   - Gradio UI (メインプロセス)

### 料金について

Docker Spaceの月額料金:

| Hardware | 料金/月 | RAM | CPU | 推奨用途 |
|----------|---------|-----|-----|----------|
| CPU basic | $0 | 16GB | 2 vCPU | ❌ Docker不可 |
| **CPU upgrade** | **$9** | 16GB | 8 vCPU | ✅ 推奨 |
| T4 small | $60 | 16GB | 4 vCPU + GPU | 不要 |

**推奨:** CPU upgrade ($9/月) で十分です

---

## トラブルシューティング

### Gradio Space

#### ビルドエラー: ModuleNotFoundError

**問題**: `ModuleNotFoundError: No module named 'mcp'`

**解決策**:
- `mcp/` ディレクトリがアップロードされているか確認
- `mcp/__init__.py` が存在するか確認

#### MCP Server起動失敗

**問題**: MCP serverがポート8000で起動しない

**解決策**:
- `app.py` のタイムアウトを増やす（`time.sleep(5)`）
- HuggingFace Spacesのログを確認

### Docker Space

#### Dockerビルドが失敗する

**問題**: `failed to solve: process "/bin/sh -c ..."`

**解決策**:
- Dockerfileの構文を確認
- ベースイメージ `python:3.10-slim` が利用可能か確認
- ビルドログで詳細なエラーを確認

#### IPFSが起動しない

**問題**: `IPFS daemon failed to start`

**解決策**:
- Dockerfile内のIPFSバージョンを確認（最新版を使用）
- `ipfs init` が正常に実行されているか確認
- `/root/.ipfs` ディレクトリが作成されているか確認

#### アンカリングボタンを押してもエラー

**問題**: `IPFS connection failed`

**解決策**:
```bash
# Spacesのログで確認すべき項目:
# 1. IPFS daemonが起動しているか
✅ IPFS is ready

# 2. MCPサーバーが起動しているか
✅ MCP server started

# 3. 環境変数が正しく設定されているか
IPFS_API_URL=/ip4/127.0.0.1/tcp/5001/http
```

#### XRPLアンカリングが失敗

**問題**: `XRPL transaction failed`

**解決策**:
1. Secrets に `XRPL_SEED` が設定されているか確認
2. Testnetアカウントに十分なXRPがあるか確認（Faucetで再取得）
3. ログでXRPL接続エラーを確認

---

## セキュリティ上の注意

### Gradio Space（無料版）

⚠️ **絶対にしないこと**:
- 秘密鍵（XRPL_SEED）を環境変数に設定しない
- `.env` ファイルをアップロードしない
- 本番データを使用しない

✅ **推奨事項**:
- README に制限事項を明記
- テストデータのみを使用するよう促す
- 入力にPII（個人情報）を含めないよう警告

### Docker Space（有料版）

✅ **安全な秘密鍵管理**:
- Spaces **Secrets** 機能を使用（環境変数として注入）
- Testnetアカウントのみを使用
- Mainnetシードは**絶対に**使用しない

✅ **IPFSセキュリティ**:
- Dockerfileで内部アクセスのみ許可（`127.0.0.1`）
- 外部からのIPFS APIアクセスをブロック
- Gateway も内部のみ

---

## パフォーマンス最適化

### メモリ使用量の削減

```python
# ログファイルサイズの制限
MAX_LOG_SIZE = 1_000_000  # 1MB

def cleanup_old_logs():
    import glob
    logs = glob.glob("logs/*.jsonl")
    if len(logs) > 10:  # Keep last 10 files
        oldest = sorted(logs)[0]
        os.remove(oldest)
```

### 起動時間の短縮

Docker Spaceの場合、初回起動が遅い可能性があります:

```dockerfile
# Dockerfile でキャッシュを活用
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# ↑ requirements.txtが変更されない限りキャッシュされる

COPY . .
# ↑ アプリケーションコードの変更時のみ再実行
```

---

## モニタリング

### ログの確認

HuggingFace Spaces UI → "Logs" タブ:
- アプリケーションの起動ログ
- IPFS daemon のログ
- MCP server のログ
- エラーメッセージ

### 使用統計

HuggingFace Spaces UI → "Analytics":
- アクセス数
- 使用時間
- リージョン別アクセス

---

## デプロイ後のテスト

### 基本機能テスト

1. **MCPツールが動作するか**
   - "Calculate 25 * 4" と入力
   - 正しく計算結果が返ってくるか確認

2. **統計が表示されるか**
   - 右パネルに "Total Tool Calls" が表示されるか

3. **ログが生成されるか**
   - 数回チャット後、`logs/events.jsonl` が作成されるか

### Docker Space専用テスト

4. **IPFSアップロードが動作するか**
   - "Anchor Session Logs" ボタンをクリック
   - IPFS CIDが表示されるか

5. **XRPLアンカリングが動作するか**
   - トランザクションハッシュが表示されるか
   - XRPL Explorer リンクが動作するか

6. **検証が動作するか**
   - トランザクションハッシュを入力
   - 検証結果が "PASSED" になるか

---

## 完全な例

### Gradio Space最小構成

```
a2a-mcp-demo/
├── app.py
├── requirements.txt
├── README.md (README_SPACES.mdから)
├── .spacesconfig.yaml
├── mcp/
└── a2a_anchor/
```

### Docker Space完全構成

```
a2a-mcp-full/
├── Dockerfile
├── app.py
├── requirements.txt
├── README.md (README_SPACES.mdから)
├── .spacesconfig.yaml (docker用)
├── mcp/
└── a2a_anchor/
```

---

## サンプルSpace

実際のデプロイ例:

**Gradio Space（無料）:**
- URL: `https://huggingface.co/spaces/YOUR_USERNAME/a2a-mcp-demo`
- 機能: MCPツールのみ

**Docker Space（有料）:**
- URL: `https://huggingface.co/spaces/YOUR_USERNAME/a2a-mcp-full`
- 機能: IPFS + XRPL フル機能

---

## 関連リンク

- **HuggingFace Spaces ドキュメント**: https://huggingface.co/docs/hub/spaces
- **Docker Spaces ガイド**: https://huggingface.co/docs/hub/spaces-sdks-docker
- **Gradio ドキュメント**: https://gradio.app/docs/
- **本プロジェクトのGitHub**: https://github.com/yourusername/A2A_xrpl_mcp

---

## サポート

問題が発生した場合:

1. HuggingFace Spaces のログを確認
2. GitHub Issues で報告: https://github.com/yourusername/A2A_xrpl_mcp/issues
3. HuggingFace Community で質問

---

**デプロイを楽しんでください！** 🚀

**推奨デプロイ:**
- **デモ/学習用** → Gradio Space（無料）
- **本格的な検証** → Docker Space（$9/月）
- **本番環境** → ローカルデプロイ（完全制御）
