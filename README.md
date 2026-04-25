# ui-kabu-reports · Atlas Quarterly Workflow 仕様書

米株四半期決算の日本語ディープダイブレポート制作リポジトリ。
各銘柄ディレクトリ（例：`BA/`, `UNH/`）に `_research/` と `FY{YY}Q{N}.html` を配置し、Cloudflare Pages で本番公開する。

本番 URL: https://atlas-financials.jp/reports/
リポジトリ: GitHub `AtlasFinancials/reports`

---

## 6 段階 + 最終チェックの制作ワークフロー

各銘柄の新規決算レポートは以下の順で制作する。**最終チェックを飛ばしてデプロイしてはならない**。

### 段階 1-4: 並列リサーチ（R1-R4）

`{TICKER}/_research/` 配下に以下を書き出す。各 15-25KB 目安、全て markdown。
並列実行推奨（Sonnet エージェント × 4）。

| ID | ファイル | 担当範囲 |
|----|---------|---------|
| R1 | `R1_financial.md` | 損益・CF・BS・セグメント・ガイダンス・経営陣発言（10-Q / 8-K / プレスリリース / トランスクリプト） |
| R2 | `R2_context.md` | 業界・マクロ・競合・規制・地政学・過去 4-8 期推移 |
| R3 | `R3_sentiment.md` | 決算後株価反応・アナリスト PT 変更・プルクォート・インサイダー・機関投資家 |
| R4 | `R4_technical.md` | 株価・MA・RSI・MACD・サポート/レジスタンス・バリュエーション |

### 段階 5: V（検証・SSOT）

`{TICKER}/_research/V_validated.md` を生成（Opus、25-40KB）。
R1-R4 の数値不一致を洗い出し、**唯一の採用値**を決定。W-2 HTML 以降はこのファイルのみを参照する。

### 段階 6: W-1（ナラティブ）

`{TICKER}/_research/W1_narrative.md` を生成（Opus、13-18KB）。
日本語本文・プルクォート 5 件・Risk/Catalyst・総合スコア（1-5）根拠。

### 段階 7: W-2（HTML 組立）

`{TICKER}/FY{YY}Q{N}.html` を生成（Opus、120-150KB）。
直近の別銘柄 HTML（例：UNH/FY26Q1.html）をベースコピー → セクション単位で差し替え。

### 段階 8: ロゴ・ファビコン準備

`logos/{TICKER}.png`（ポータル用、正方形 512x512、ブランド色）／
`logos/{TICKER}-header.png`（レポートヘッダー用、横型 800x、**白抜き**＝ダーク背景前提）／
`logos/{TICKER}-favicon.png`（64x64 シンボル、ブランド色）を作成。

### 段階 9: 🔴 最終チェック（必須・デプロイ前）

**このステップをスキップしてデプロイしてはならない**。
ブラウザで HTML を開き、Opus レビューエージェント（または人手）で以下を全項目検証する。

#### チェックリスト

##### A. テキスト品質
- [ ] 誤字脱字（日本語・英語）
- [ ] 表記ゆれ（数値フォーマット、通貨単位、社名・ティッカー）
- [ ] **前銘柄の残存用語**（例：BA 制作で "UNH", "MBR", "Optum" が残っていないか）
- [ ] 事実誤認（SSOT `V_validated.md` と全数値が一致するか）

##### B. 数値表示
- [ ] 単位（$M / $B / % / bps）の取り違え
- [ ] 符号（赤字企業は負値、正しく `-$X` 表記）
- [ ] ビート率計算（赤字縮小は正、拡大は負）
- [ ] YoY / QoQ の向き（改善 / 悪化表記の整合性）

##### C. 技術機能
- [ ] **通貨トグル**（JPY 換算ボタン）: `window.ATLAS_FX` 設定、`.no-currency` クラス付与漏れ
- [ ] **ライト / ダークモード**: CSS 変数（`--bg`, `--t1` 等）運用、HEX 直書き箇所が Dark 前提になっていないか
- [ ] **アコーディオン**: `data-accordion` 属性と `.section-body` / `.sec3-body` の対応
- [ ] **TOC（目次）**: `tocJump()` の参照先 ID が実在するか
- [ ] **Chart.js**: `canvas id` と `new Chart(document.getElementById(...))` の対応、データポイント数と labels 数の一致

##### D. リンク・参照
- [ ] 外部リンク（`href="https://..."`）の有効性
- [ ] **ロゴ参照**: `src="../logos/{TICKER}-header.png"`, `favicon href="../logos/{TICKER}-favicon.png"` が実在ファイルか
- [ ] **TradingView ウィジェット**: `"symbol": "NYSE:{TICKER}"` 設定
- [ ] **画像 alt**: 正しい会社名
- [ ] **関連朝刊リンク**: `data-ticker="{TICKER}"` になっているか
- [ ] **meta tags**: `atlas-access` の ticker

##### E. レイアウト・ユーザビリティ
- [ ] モバイル（≤768px）・デスクトップ両方で崩れていないか
- [ ] スクロール・アコーディオン展開が機能するか
- [ ] 経営陣コメント・Risk/Catalyst 項目が読みやすい順か

##### F. 標準フォーマット（全銘柄共通）
- [ ] **Layer 1 Consensus vs 実績テーブルは 3 行に統一**：
  1. 売上高
  2. Core EPS（または Adjusted EPS）
  3. 次 Q 売上ガイダンス（会社未提供なら「未提示」と明記）
- [ ] 総合スコアは 1-5 の整数、スコア根拠 HTML コメントを併記
- [ ] フッター: `{TICKER} / FY{YY} Q{N} · 発行 YYYY-MM-DD · Atlas Quarterly`

---

## 段階 10: デプロイ

`deploy_report.py` を実行：

```bash
source ~/.zshrc
python3 deploy_report.py ~/ui-kabu-reports/{TICKER}/FY{YY}Q{N}.html {TICKER} FY{YY}Q{N} {SCORE}
```

処理内容：
1. HTML コピー → ticker index.html 生成
2. Atlas nav + Quarterly バンド注入
3. ルート index.html（全銘柄ポータル）更新
4. **Cloudflare Pages 本番デプロイ**（wrangler、`CLOUDFLARE_API_TOKEN` 必須）
5. **git commit + push origin main**
6. LINE 通知ブロードキャスト（不要なら事前に確認）

### 既知の注意点

- `CLOUDFLARE_API_TOKEN` は `~/.zshrc` にのみ設定。非対話シェルでは `source ~/.zshrc` を先行実行
- wrangler が commit message 読み取りで invalid UTF-8 エラー → `--commit-dirty=false` で回避可
- ロゴ 3 種の色選択：
  - `{TICKER}.png`（ポータルカード = **light 背景**）: **ブランド色**
  - `{TICKER}-header.png`（レポートヘッダー = **dark navy 背景**）: **白抜き**
  - `{TICKER}-favicon.png`（ブラウザタブ）: **ブランド色**
- ポータルカードの `card-logo` CSS は `height:30px; max-width:44px`。**縦長アスペクトは視認不能**になるため正方形必須。

---

## セクターマッピング

`deploy_report.py` 内の `SECTOR_MAP` に銘柄追加を忘れずに。未登録だと「未分類」で表示される。

---

## 参考銘柄

最新フォーマットのベースとして使用：
- `NFLX/Q1_2026.html`（`_template_patterns.md` の正本）
- `UNH/FY26Q1.html`（最新フォーマット）
- `BA/FY26Q1.html`（最新フォーマット、BCA/BDS/BGS 3 セグメント構造）
