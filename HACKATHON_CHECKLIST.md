# 🏆 HuggingFace Hackathon 提出チェックリスト

## 📋 必須要件（Prize Eligibility）

HuggingFace Hackathonで賞を獲得するには、以下を**すべて**満たす必要があります：

### 1. Organization への参加 ✅

- [ ] Hackathon organization ページにアクセス
- [ ] "Request to join this org" をクリック
- [ ] 承認を待つ（通常数分〜数時間）
- [ ] 承認後、organization memberになったことを確認

### 2. Space を Organization に提出 ✅

- [ ] HuggingFace Spaceを作成（Gradio または Docker）
- [ ] Space設定で organization を選択
- [ ] または、既存Spaceを organization に移動

### 3. Track Tags を README に追加 ✅

**README_HACKATHON.md を Space の README.md としてアップロード**

必須タグ（該当するものを選択）:
```markdown
**Tracks Entered:**
- `#building-with-mcp` - MCPサーバー/ツールを構築
- `#mcp-in-action` - MCPを使った実用アプリケーション
```

**このプロジェクトの推奨タグ:**
```markdown
**Tracks Entered:**
- `#building-with-mcp` - Custom MCP server with 5 tools + hybrid logging
- `#mcp-in-action` - Blockchain-anchored AI audit trails
```

### 4. Social Media 投稿リンク ✅

- [ ] Twitter、LinkedIn、またはその他SNSにプロジェクトを投稿
- [ ] 投稿に以下を含める:
  - プロジェクトの説明
  - HuggingFace Space へのリンク
  - ハッシュタグ（例: #HuggingFaceHackathon #MCP）
- [ ] 投稿URLをREADMEに追加

**投稿例（Twitter）:**
```
🔐 Just submitted my project to @huggingface MCP Hackathon!

A2A Trace Logger: Making AI agents accountable with blockchain 🔗

✅ MCP tool logging
✅ IPFS storage
✅ XRPL anchoring
✅ Full verification

Try it: [Space URL]
Code: https://github.com/niikun/A2A_xrpl_mcp

#HuggingFaceHackathon #MCP #Blockchain #AITransparency
```

### 5. 締め切り前に提出 ✅

- [ ] **Deadline: November 30, 2025, 11:59 PM UTC**
- [ ] 時間に余裕を持って提出（最終日を避ける）
- [ ] すべてのファイルが正しくアップロードされているか確認

---

## 🚀 デプロイ手順

### オプション A: Gradio Space（無料・簡単）

#### ステップ1: Spaceを作成

1. https://huggingface.co/new-space にアクセス
2. 以下を入力:
   - **Owner**: Hackathon organization を選択
   - **Space name**: `a2a-mcp-demo` (または任意の名前)
   - **License**: Apache 2.0
   - **SDK**: Gradio
   - **Hardware**: CPU basic（無料）
3. "Create Space" をクリック

#### ステップ2: ファイルをアップロード

以下のファイルをアップロード:

```
必須ファイル:
- app.py
- requirements.txt
- .spacesconfig.yaml
- README_HACKATHON.md → README.md にリネーム

プロジェクトファイル:
- mcp/ (フォルダ全体)
- a2a_anchor/ (フォルダ全体)
```

**アップロード方法:**

**方法1: Web UI（推奨）**
1. Spaceページの "Files" タブ
2. "Add file" → "Upload files"
3. すべてのファイルをドラッグ&ドロップ
4. Commit message: "Initial submission for MCP Hackathon"
5. "Commit changes to main"

**方法2: Git CLI**
```bash
# 1. Spaceをクローン
git clone https://huggingface.co/spaces/HACKATHON_ORG/a2a-mcp-demo
cd a2a-mcp-demo

# 2. ファイルをコピー
cp /path/to/A2A_xrpl_mcp/app.py .
cp /path/to/A2A_xrpl_mcp/requirements.txt .
cp /path/to/A2A_xrpl_mcp/.spacesconfig.yaml .
cp /path/to/A2A_xrpl_mcp/README_HACKATHON.md README.md
cp -r /path/to/A2A_xrpl_mcp/mcp .
cp -r /path/to/A2A_xrpl_mcp/a2a_anchor .

# 3. コミット
git add .
git commit -m "Initial submission for MCP Hackathon"
git push
```

#### ステップ3: READMEを更新

README.md内の以下を更新:

```markdown
**Social Media Post:** `[YOUR_ACTUAL_POST_URL_HERE]`
```

#### ステップ4: ビルド確認

1. Space ページで "Building..." → "Running" になるのを待つ
2. ログでエラーがないか確認
3. UIが正常に表示されるか確認
4. MCPツールが動作するかテスト

---

### オプション B: Docker Space（完全機能・有料）

完全なIPFS + XRPL機能を含める場合:

#### ステップ1: Spaceを作成

1. https://huggingface.co/new-space にアクセス
2. 以下を入力:
   - **Owner**: Hackathon organization を選択
   - **Space name**: `a2a-mcp-full`
   - **License**: Apache 2.0
   - **SDK**: **Docker** ← 重要！
   - **Hardware**: **CPU upgrade**（$9/月）
3. "Create Space" をクリック

#### ステップ2: ファイルをアップロード

```
必須ファイル:
- Dockerfile
- app.py
- requirements.txt
- .spacesconfig-docker.yaml → .spacesconfig.yaml にリネーム
- README_HACKATHON.md → README.md にリネーム

プロジェクトファイル:
- mcp/ (フォルダ全体)
- a2a_anchor/ (フォルダ全体)
```

#### ステップ3: Secretsを設定

1. Space Settings → Repository secrets
2. 以下を追加:

```
Name: XRPL_SEED
Value: sXXXXXXXXXXXXXXXXXXXXXXX
```

**取得方法:**
- https://xrpl.org/xrp-testnet-faucet.html
- "Generate Faucet Credentials" をクリック
- Secret をコピー

⚠️ **Testnetのseedのみ使用！**

#### ステップ4: ビルドとテスト

1. Dockerビルドが完了するまで待つ（5-10分）
2. ログで確認:
   ```
   ✅ IPFS is ready
   ✅ MCP server started
   🌐 Starting Gradio UI...
   ```
3. "Anchor Session Logs" ボタンをテスト
4. XRPL Testnet Explorerでトランザクションを確認

---

## 📝 README更新内容

### 必須項目

README_HACKATHON.md の以下のセクションを更新:

```markdown
## 🏆 HuggingFace Hackathon Submission

**Hackathon:** MCP 1st Birthday Hackathon (November 2025)

**Tracks Entered:**
- `#building-with-mcp` - Custom MCP server with 5 tools + hybrid logging system
- `#mcp-in-action` - Real-world application: Blockchain-anchored AI audit trails

**Social Media Post:** https://twitter.com/YOUR_USERNAME/status/YOUR_POST_ID
<!-- ↑ 実際の投稿URLに置き換える -->

**Team:** niikun (Solo)

**Demo:** This Space

**Full Source:** https://github.com/niikun/A2A_xrpl_mcp
```

---

## ✅ 提出前最終チェック

### 技術的チェック

- [ ] Space が正常にビルドされる
- [ ] Gradio UIが表示される
- [ ] MCPツールが動作する（"Calculate 25 * 4" をテスト）
- [ ] 統計パネルが表示される
- [ ] ログが生成される
- [ ] （Docker版のみ）IPFS/XRPLアンカリングが動作する

### ドキュメントチェック

- [ ] README.mdにHackathon submitセクションがある
- [ ] Track tagsが正しく記載されている
- [ ] Social media post URLが記載されている
- [ ] GitHub リポジトリリンクが正しい
- [ ] ライセンスが明記されている（Apache 2.0）

### Organization チェック

- [ ] Hackathon organization のメンバーになっている
- [ ] Space が organization に所属している
- [ ] Space が public に設定されている

### 締め切りチェック

- [ ] 現在日時が締め切り前である
- [ ] すべてのコミットがpushされている
- [ ] Space のステータスが "Running" である

---

## 🎬 デモビデオ（オプション）

審査員へのアピールのため、短いデモビデオを作成することを推奨:

1. **録画内容（2-3分）:**
   - プロジェクトの紹介
   - MCPツールを使ったチャットデモ
   - （Docker版）アンカリングとXRPL Explorer確認
   - 技術的なハイライト

2. **アップロード先:**
   - YouTube（Unlisted）
   - Loom
   - HuggingFace Space の README に埋め込み

3. **README への追加:**
```markdown
## 🎬 Demo Video

Watch the 2-minute demo: [YouTube Link]()
```

---

## 📊 審査基準（参考）

Hackathonでは以下が評価されると予想:

1. **Innovation（革新性）**
   - MCPとブロックチェーンの組み合わせ ✅
   - A2A標準への準拠 ✅
   - Merkle Root検証 ✅

2. **Technical Implementation（技術的実装）**
   - 動作するデモ ✅
   - コード品質 ✅
   - ドキュメント完備 ✅

3. **Usefulness（有用性）**
   - 実世界の問題を解決 ✅（監査・コンプライアンス）
   - スケーラビリティ ✅
   - 教育的価値 ✅

4. **Presentation（プレゼンテーション）**
   - わかりやすいREADME ✅
   - インタラクティブデモ ✅
   - 視覚的な説明 ✅（demo_interactive.html）

---

## 🔗 参考リンク

- **Hackathon 公式ページ**: https://huggingface.co/MCP-1st-Birthday
- **Space 作成ガイド**: https://huggingface.co/docs/hub/spaces
- **Docker Space ガイド**: https://huggingface.co/docs/hub/spaces-sdks-docker
- **このプロジェクトの完全ドキュメント**: [README.md](README.md)

---

## 💡 トラブルシューティング

### Space がビルドに失敗する

**エラー:** `ModuleNotFoundError: No module named 'mcp'`

**解決策:**
```bash
# mcp/ ディレクトリ全体がアップロードされているか確認
# mcp/__init__.py が存在するか確認
```

### IPFS/XRPLが動作しない（Docker版）

**解決策:**
1. Logs タブで IPFS daemon が起動しているか確認
2. Secrets に XRPL_SEED が設定されているか確認
3. Hardware が CPU upgrade 以上であるか確認

### Organization に参加できない

**解決策:**
1. "Request to join" をクリック後、承認を待つ
2. Hackathon期間中であることを確認
3. 承認されない場合、Hackathon運営に問い合わせ

---

## 🎉 提出後

提出が完了したら:

1. ✅ Space URLを保存
2. ✅ ソーシャルメディアで宣伝
3. ✅ Community feedback を確認
4. ✅ 必要に応じて改善を継続
5. ✅ 審査結果を待つ

**Good luck! 🚀**

---

**次のステップ:** [HUGGINGFACE_DEPLOYMENT.md](HUGGINGFACE_DEPLOYMENT.md) で詳細なデプロイ手順を確認
