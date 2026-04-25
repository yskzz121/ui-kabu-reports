# 引き継ぎ書: INTC Q1 2026 Atlas Quarterly 決算レポート

**作成日**: 2026-04-24
**作成者**: Claude Code（前任セッション）
**対象プロジェクト**: Atlas Quarterly 米国株決算レポート
**対象銘柄**: Intel Corporation（NASDAQ: INTC）
**対象四半期**: Q1 2026（四半期末 2026-03-28、発表 2026-04-23）

---

## 1. プロジェクト概要

Atlas Quarterly の 4エージェント並列ワークフロー（R1-R4 → V → W-1/W-2 → DB → デプロイ）で、Intel の Q1 2026 決算分析 HTML レポートを生成中。

- **ワークフロー仕様**: `~/CLAUDE.md.bak`（Single Source of Truth）
- **デザイン雛形**: `~/ui-kabu-reports/TSM/Q1_2026.html`（Atlas Quarterly 新フォーマット v2）
- **出力先**: `~/ui-kabu-reports/INTC/Q1_2026.html`
- **本番公開先（予定）**: `https://atlas-financials.jp/reports/INTC/Q1_2026.html`

---

## 2. 進捗ステータス

| Phase | 内容 | モデル | 状態 |
|---|---|---|---|
| 1-R1 | 財務データリサーチ | Sonnet | ✅ 完了 |
| 1-R2 | 外部環境リサーチ | Opus | ✅ 完了 |
| 1-R3 | センチメントリサーチ | Sonnet | ✅ 完了 |
| 1-R4 | テクニカル分析 | Sonnet | ✅ 完了 |
| 2 | Agent V 検証・スコア確定 | Opus 1M | ✅ 完了 |
| 3-W1 | ナラティブ執筆 | Opus | ✅ 完了 |
| 3-W2 | HTML 組立 | Sonnet | ✅ 完了 |
| — | **ブラウザ目視確認** | — | ⏸ ユーザー確認待ち |
| 4 | 決算DB（xlsx）追記 | Haiku | ⏹ 未着手 |
| 5 | デプロイ（`deploy_report.py`） | — | ⏹ 未着手 |

**次の一手**: ユーザーの目視確認 → 修正反映 → Phase 4-5 へ。

---

## 3. 確定事項（Agent V 検証済み）

### 3.1 総合評価スコア

- **スコア: 5🚀（素晴らしい決算）** ← ユーザー承認済（2026-04-24）
- ユーザー指示:「リスク警告はしっかりつけて」

### 3.2 主要財務数値（Q1 2026）

| 指標 | 値 | コメント |
|---|---|---|
| 売上高 | $13,580M（+6.9% YoY、-0.9% QoQ） | コンセンサス $12.42B を +9.3% ビート |
| Non-GAAP EPS | $0.29（+123% YoY） | コンセンサス $0.01 の **29倍** |
| GAAP EPS | $(0.73) | Mobileye のれん減損 $4.1B 含む（非現金・一過性） |
| Non-GAAP 粗利率 | 41.0% | ガイダンス比 **+650bp** 上振れ |
| Non-GAAP 営業利益率 | 12.3% | 前年 5.4% → +6.9pp |
| 営業CF | $1,096M | |
| Gross CapEx | $5,000M | |
| 調整後 FCF | $(2,016)M | |
| 現金+短期投資 | $32,789M | |
| 有利子負債合計 | $45,031M | |

### 3.3 セグメント別（Q1 2026）

| セグメント | 売上 | YoY | 備考 |
|---|---|---|---|
| CCG（クライアント） | $7,700M | +1.3% | OPM 32.6% |
| DCAI（データセンター・AI） | $5,100M | **+22.0%** | OPM 推計 30.5%、AI 主導売上 60% |
| Intel Foundry | $5,400M | +15.9% | OPM -45.0%（前期 -55.7%、**+10.7pp 改善**）、外部売上 $174M（全体の 3.2%） |
| All Other（Mobileye 含む） | $628M | — | |

### 3.4 Q2 2026 ガイダンス

| 項目 | ガイダンス | コンセンサス | ビート率 |
|---|---|---|---|
| 売上 | $13.8-14.8B（中央 $14.3B） | $13.07B | +9.4% |
| Non-GAAP EPS | $0.20 | $0.06-0.09 | +122-233% |
| Non-GAAP 粗利率 | 39.0% | — | — |

**6四半期連続ガイダンス上振れ**（CFO Zinsner 発言）

### 3.5 バリュエーション3シナリオ（Agent V 算出）

| シナリオ | EPS 前提 | PER | 想定株価 | vs 終値 $66.78 | 判定 |
|---|---|---|---|---|---|
| LOW | FY26 EPS $0.51 × 12x | 12x | **$6.1** | -90.9% | 極端に割高 |
| MID | FY27 EPS $1.03 × 30x | 30x | **$30.9** | -53.7% | 割高 |
| HIGH | FY27 EPS $1.34 × 50x | 50x | **$67.0** | +0.3% | ほぼ適正/やや割高 |

- **NTM Fair Value**: $48-62（中央値 $55）
- **現時点の判定**: AH $77.5 は「割高〜極端に割高」、FY28 期待を一部先取り
- **Forward PER**: 124x（GuruFocus、FY26 EPS $0.51 ベース）
- **PSR**: 6.2x（終値）/ 7.4x（AH）

### 3.6 株価

- 通常終値（2026-04-23）: **$66.78**（+2.3%）、日中高値 $78.10
- AH: $75-80（+12-20%）、中央値 $77.50
- 52週: 安値 $18.97 / 高値 $78.10
- YTD: +76%（SOX +44.7% を 30pp 上回る）
- 時価総額: $335B（AH $400B）
- 2026-04-23 は **26年ぶりに 2000年 ATH $75.81 を突破**

### 3.7 アナリスト反応（決算後）

- カバレッジ 31-37 名、コンセンサス **Hold**
- 平均 PT: $51（決算前後改定途上値）
- 決算後改定済 PT レンジ: $55-$95（最高 HSBC $95、最低 Wells Fargo $55）
- **AH 株価 $77.5 がアナリスト平均 PT を 52% 上回る乖離** → 織り込み超過警戒
- 決算後格上げ: HSBC（Hold→Buy $50→$95）、Morgan Stanley（EW→OW $41→$56）、BNP、Raymond James、Citi 新規Buy、Northland $54→$92
- 格下げ: KGI（Outperform→Neutral、「織り込み済み」）

### 3.8 テクニカル

- RSI(14): 78（過熱、AH後 80-85 想定）
- SMA 50 乖離: +32.6%、SMA 200 乖離: **+75.0%**
- ADX 39（強トレンド）、MACD 強気ヒストグラム+
- Short Float: 2.81%（低水準）、Days to Cover 1.17日
- ゴールデンクロス継続（2025-08-15 以降）
- 判定: **強気だが短期過熱注意**（IV crush リスク）

### 3.9 経営陣キーコメント

- **Lip-Bu Tan CEO**:
  - 「CPUは AIスタック全体のオーケストレーション層」
  - 「18A ウェーハは社内予測を上回るペース」
  - 「14A の同時期成熟度は 18A を上回る」
  - 「TSMC は重要なパートナー、マルチファウンドリーアプローチを採用」
- **David Zinsner CFO**:
  - 「AI主導ビジネスは売上の60%、+40% YoY」
  - 「先進パッケージング需要は数億ドル → 年間数十億ドルへ」
  - 「2026 CapEx は前年比横ばい（前回ガイダンスから上方修正）」
  - 「下半期 PC TAM は low double-digit % down」← 下期リスク警告

---

## 4. 生成物一覧

### 4.1 メインファイル

| パス | 内容 | サイズ |
|---|---|---|
| `~/ui-kabu-reports/INTC/Q1_2026.html` | レポート本体（Atlas Quarterly 新フォーマット v2） | 1,869行 / 129KB |
| `~/ui-kabu-reports/INTC/HANDOVER.md` | 本引き継ぎ書 | — |

### 4.2 デザイン仕様遵守チェック結果（2026-04-24 時点）

| 項目 | 実測 |
|---|---|
| Atlas Navy `#0F1829` | 12 箇所 ✅ |
| Shippori Mincho B1 見出し | 15 箇所 ✅ |
| layer-eyebrow（3層構造） | 4 箇所 ✅ |
| panel-merge パターン | 25 箇所 ✅ |
| risk-card 構造 | 17 箇所 ✅ |
| `.hl` 強調（Layer II 5項目） | 10 個 ✅ |
| score-high（金色シマー） | 3 箇所 ✅ |
| val-warning（赤系警告ボックス） | 5 箇所 ✅ |
| TradingView `NASDAQ:INTC` | 1 箇所 ✅ |
| 絵文字は 🚀 と ⚠️ のみ | 確認済 ✅ |

---

## 5. 残課題

### 5.1 デプロイ前に対応必須

1. **`~/ui-kabu-reports/logos/INTC.svg` 未配置**
   - 現状: `<img class="rh-logo" src="../logos/INTC.svg" alt="Intel">` タグは記述済
   - 暫定: `rh-ticker` バッジ + `h1 Intel Corporation` でテキスト識別可
   - 対応: Intel 公式ブランド SVG を取得し `logos/` 配下に配置

2. **7Q 推移の過去値で推定値混入**
   - **売上 / EPS は一次ソース確認済**（問題なし）
   - **Cash Flow 7Q（営業CF / CapEx）と Non-GAAP 粗利率 7Q 推移は W-2 が推定値を使用**
   - Agent V の引き渡しに過去 CF/Margin データが含まれていなかったため
   - 対応: 決算DB（`~/Desktop/決算分析/企業決算DB/企業決算DB_Earnings_Database.xlsx`）または SEC EDGAR から過去値を取得して差替

3. **地域別売上（Q1 2026 単独）**
   - 現状: Intel は Q1 プレスリリースで地域別開示なし、FY2025 通期のみ参考表記
   - 対応: 10-Q（通常 5月初旬提出）後に更新推奨

### 5.2 ユーザー確認待ち

- **ブラウザ目視確認** — 2026-04-24 時点で `open` コマンドで起動済、ユーザーフィードバック待ち
- 確認ポイント:
  - Header ロゴ欠落の見え方
  - Layer I スコアバッジ（金色シマー animation）
  - Layer II「今回のポイント」5項目の密度
  - ⚠️ 注意喚起ボックス（Valuation 直下、赤系）の目立ち具合
  - TradingView ウィジェット読み込み
  - アコーディオン展開動作
  - ダーク/ライトテーマ切替（🌙/☀️）

### 5.3 Phase 4-5（未実施）

**Phase 4: 決算DB追記**
- 対象ファイル: `~/Desktop/決算分析/企業決算DB/企業決算DB_Earnings_Database.xlsx`
- シート: 決算サマリーDB / バリュエーション / SaaS KPI
- 推奨モデル: Haiku 4.5（CSV追記・機械的処理）
- INTC は DB 未登録銘柄なので**新規エントリ作成**

**Phase 5: GitHub Pages デプロイ**
- コマンド例:
  ```bash
  python3 ~/ui-kabu-reports/deploy_report.py \
    ~/ui-kabu-reports/INTC/Q1_2026.html \
    INTC \
    Q1_2026 \
    5 \
    "Non-GAAP EPS が予想の29倍、6四半期連続ガイダンス上振れ。ただしForward PER 124xで織り込み超過警戒"
  ```
- 自動処理: 銘柄別index・ポータルindex更新 → git push → GitHub Pages 公開
- **LINE通知はデプロイスクリプトから自動送信しない方針**（CLAUDE.md.bak §1 運用ルール）
- 公開後、ユーザーが内容確認・修正完了後に手動で LINE Atlas グループへ貼付

---

## 6. 重要な判断ポイント（将来の再検討用）

### 6.1 スコア判定の分岐

「5🚀 素晴らしい決算」か「4📈 良い決算」かでユーザーに選択肢を提示 → **5 で確定**。

- ✅ 5 寄り根拠: Non-GAAP 3段ビート（売上・EPS・ガイダンス）+ マージン +650bp 上振れ + 6四半期連続上振れ + AI 売上比率 60%・+40% YoY
- ⚠️ 4 寄り懸念: GAAP EPS $(0.73)、調整後 FCF $(2.0)B、Mobileye のれん減損 $4.1B、PC TAM 下期 -10-15% 警告
- 結論: 減損は非現金・将来 EPS 影響限定との理由で 5 確定、**リスク警告を厚めに配置する設計で中和**

### 6.2 バリュエーション表記の難しさ

- Forward PER 124x は「赤字回復過程の異常値」
- 過去黒字期（2017-2021）Intel 平均 PER 12-15x との比較では「極端に割高」
- AI 半導体プレミアム期の適用上限 25-35x（AMD）、35-45x（NVDA）と比較しても突出
- **投資推奨には読めない中立表現を維持**、Risk Top 1 + ⚠️ 警告ボックスで3層強調

### 6.3 データ矛盾の解決

Agent V が以下を確定:

| 項目 | 矛盾源 | 採用値 |
|---|---|---|
| 52週高値 | R3 $78.10 vs R4 $75.81 | $78.10（決算日中新高値）、$75.81（前日まで旧ATH）の両方明示分離 |
| Forward PER | 91x（FinBox）/ 124x（GuruFocus）/ 134x（R3 上限） | **124x** 採用（FY26 EPS $0.51 ベース検算一致） |
| アナリスト平均 PT | $49.68-53（改定途上）vs 最低 Wells Fargo $55 | 平均 $51（改定途上）/ 決算後改定済 $55-$95 レンジ |

---

## 7. 参考情報

### 7.1 主要データソース URL

- **Intel Q1 2026 プレスリリース（一次）**: https://www.intc.com/news-events/press-releases/detail/1767/intel-reports-first-quarter-2026-financial-results
- **Motley Fool 決算コール書き起こし**: https://www.fool.com/earnings/call-transcripts/2026/04/23/intel-intc-q1-2026-earnings-transcript/
- **AlphaStreet 書き起こし**: https://news.alphastreet.com/intel-corporation-intc-q1-2026-earnings-call-transcript/
- **CNBC 決算レポート**: https://www.cnbc.com/2026/04/23/intel-intc-q1-2026-earnings-report.html

### 7.2 内部参照

- **仕様SOT**: `~/CLAUDE.md.bak`（§1 ワークフロー、§3 スコア、§7 バリュエーション、§4-5 分析項目）
- **デザイン雛形**: `~/ui-kabu-reports/TSM/Q1_2026.html`（Atlas Quarterly 新フォーマット v2、2244行）
- **Wiki**: `~/projects-wiki/projects/investment-reports.md`（Atlas 投資分析概要）
- **決算DB**: `~/Desktop/決算分析/企業決算DB/企業決算DB_Earnings_Database.xlsx`
- **デプロイスクリプト**: `~/ui-kabu-reports/deploy_report.py`

### 7.3 Agent セッション ID（再呼び出し用）

| エージェント | ID | 備考 |
|---|---|---|
| R1 財務 | `a04014494680691b8` | SendMessage で再起動可 |
| R2 外部環境 | `ab8a87fb8b4f923ee` | |
| R3 センチメント | `a6110594aa360c27e` | |
| R4 テクニカル | `a2124bfdf6a00351b` | |
| V 検証 | `aee55353f793c8f8d` | |
| W-1 ナラティブ | `a15a28e29f7bf8e6a` | |
| W-2 HTML 組立 | `aff605dff83f0c826` | 追加データ渡しの差替に利用可 |

---

## 8. セッション再開時の具体的アクション

### 8.1 状態確認コマンド

```bash
# ファイル存在確認
ls -la ~/ui-kabu-reports/INTC/
# → Q1_2026.html（1,869行）, HANDOVER.md が存在するはず

# ブラウザ目視
open ~/ui-kabu-reports/INTC/Q1_2026.html

# ロゴ配置確認
ls ~/ui-kabu-reports/logos/ | grep -i intc
# → 未配置（要対応）
```

### 8.2 推奨される次のステップ

1. **ユーザーに目視確認結果をヒアリング**（修正要否）
2. **修正がある場合**: W-2 セッション（ID `aff605dff83f0c826`）に SendMessage で差分指示 → 再生成
3. **修正なしで承認された場合**:
   - `INTC.svg` ロゴ配置（Intel ブランドサイトから取得）
   - Phase 4: 決算DB 追記（Haiku）
   - Phase 5: `deploy_report.py` 実行
4. **デプロイ後**: 公開URL と総合評価コメントをユーザーに提示、LINE 貼付は**ユーザー手動**

### 8.3 デプロイ時のコメント案（LINE 貼付用）

```
INTC Q1 2026 決算分析（スコア 5🚀 素晴らしい決算）
• 売上 $13.58B（コンセンサス +9.3%）、Non-GAAP EPS $0.29（予想 $0.01 の29倍）
• Non-GAAP 粗利率 41.0%（ガイダンス +650bp 上振れ）、DCAI +22% YoY
• Q2 ガイダンス売上 $14.3B 中央値で +9.4% 上振れ、6四半期連続ガイダンス上方修正
• ⚠️ Forward PER 124x、アナリスト平均 PT $51 と AH $77.50 の乖離52%で織り込み超過警戒
公開: https://atlas-financials.jp/reports/INTC/Q1_2026.html
```

---

## 9. ワークフロー固有の注意事項（次回同種作業時）

- **Phase 1 R1-R4 は必ず同一メッセージ内で4つの Agent tool calls として並列発火**（CLAUDE.md.bak §1 「並列発火ルール」）
- **キャッシュ戦略**: Phase 2-3 を5分以内に連続実行するとプロンプトキャッシュヒット（Brand Book + TSM 雛形 + 過去7Q DB）
- **R1-R4 の生データを W-1/W-2 に直接渡さない** — V が統合・検証した構造化データのみ渡す（約40% トークン削減）
- **デザイン雛形踏襲**: TSM/Q1_2026.html を Read で全文読み → class名・CSS・構造を保持したままデータのみ置換
- **絵文字禁止** — スコアアイコン（🚀📈⏸️📉👎）と UI 機能記号（🌙/☀️、☰、⚠️、国旗）のみ例外

---

**引き継ぎ書 終わり**
