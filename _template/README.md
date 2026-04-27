# Atlas Quarterly Master Template

**初版**: 2026-04-27
**最新更新**: 2026-04-27（IBM Q1 2026 由来）

このディレクトリは Atlas Quarterly 決算レポートの **常に最新仕様** を保持する master template 置き場。

## ファイル

- `quarterly-master.html` — Atlas Quarterly レポート HTML 雛形（プレイヤー実装版・新仕様準拠）

## 使い方（新規銘柄制作時）

```bash
TICKER=AAPL
PERIOD=Q2_2026
mkdir -p ~/ui-kabu-reports/$TICKER
cp ~/ui-kabu-reports/_template/quarterly-master.html ~/ui-kabu-reports/$TICKER/$PERIOD.html
```

その後、Python 部分置換 or Edit ツールで以下を新銘柄向けに書き換える：

- 銘柄名・ティッカー・期表示・発表日（`<header class="rh">` 内）
- ロゴ参照（`../logos/<TICKER>.png` または `.svg`）
- og:title / og:description / atlas-access の ticker 値
- 全14セクションの数値・コメント・チャート data
- ラジオプレーヤー: `<PERIOD>-radio.mp3` と chapters JSON
- フッターの企業名・発行日・ID

## 由来（master の更新履歴）

| 日付 | 由来 | 取り込んだ改善 |
|---|---|---|
| 2026-04-27 | IBM Q1 2026 | ヘッダープレイヤー版新仕様（68px/176px/order:3/絶対URL+1200w化 JS） |

新仕様が確立されたら、新規 master を作成して上書き：

```bash
cp ~/ui-kabu-reports/<最新確認済み銘柄>/<PERIOD>.html ~/ui-kabu-reports/_template/quarterly-master.html
# README.md の更新履歴に追記
```

## 関連仕様

- `~/projects-wiki/specs/atlas-quarterly-header.md` — ヘッダーレイアウト仕様（9章）
- `~/projects-wiki/specs/atlas-quarterly-radio.md` — ラジオ版生成仕様
- `~/projects-wiki/specs/atlas-quarterly-handoff-20260427-header.md` — 引き継ぎ書
- `~/CLAUDE.md.bak` — Atlas Quarterly 仕様マスター（1423行・3レイヤー構造等）
- メモリ `feedback_html_generation_pattern.md` — cp+Edit パターン
