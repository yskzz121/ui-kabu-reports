# NFLX新フォーマット 軽量テンプレート
# 各セクションのHTML構造パターンのみ抽出（データは銘柄ごとに差し替え）
# 正本: ~/ui-kabu-reports/NFLX/Q1_2026.html


============================================================
l1 (65 lines, showing first 35)
============================================================
<section class="l1">
<!-- Score -->
<div class="l1-score">
<div class="l1-score-badge">
<span class="l1-score-num">3</span>
<span class="l1-score-label">悪くない決算</span>
</div>
</div>
<!-- Consensus vs 実績 (統合) -->
<div class="l1-consensus">
<div class="l1-consensus-head">Consensus vs 実績（Q1 2026）</div>
<table class="l1-consensus-tbl">
<thead>
<tr>
<th>項目</th>
<th>コンセンサス</th>
<th>実績</th>
<th>ビート率</th>
</tr>
</thead>
<tbody>
<tr>
<td class="lbl">売上高 / Revenue</td>
<td class="cn">$12.18B</td>
<td class="val">$12.25B</td>
<td class="beat"><span class="beat-lamp"></span>+0.6% <span class="beat-text">ビート</span></td>
</tr>
<tr>
<td class="lbl">EPS（Diluted, GAAP）</td>
<td class="cn">$0.76</td>
<td class="val">$1.23</td>
<td class="beat"><span class="beat-lamp"></span>+61.8% <span class="beat-text">ビート※</span></td>
</tr>
<tr>
<td class="lbl">Q2 2026 売上ガイダンス</td>
...

============================================================
sec-risk (39 lines)
============================================================
<section class="sec3" data-accordion="" id="sec-risk">
<div class="sec3-title">Risk &amp; Catalyst <span class="jp">· リスク・注目ポイント / カタリスト</span></div>
<div class="sec3-body">
<div class="risk-grid">
<div class="risk-card">
<h4>Positive Catalysts</h4>
<ul class="risk-top">
<li>広告事業の倍増（2026年 ~$3B）— AVOD MAV 190M・広告主4,000社超</li>
<li>FCF ガイダンス上方修正（$11B → $12.5B）+ 自社株買い継続（残り$6.8B）</li>
<li>4地域すべてで YoY 二桁成長、APAC +19.9% / LATAM +18.6% が牽引</li>
</ul>
<ul class="risk-more">
<li>スポーツ拡大 — NFL クリスマス、WWE Raw ($5B/10年)、ボクシング、FIFA女子W杯 2027/2031 独占</li>
<li>価格改定余力 — 米・スペイン値上げを「好調」と経営陣評価</li>
<li>2030年長期ビジョン — 時価総額 $1T / 売上 $80B / 営業益 $30B</li>
<li>生成AI広告を2026年全AVOD市場で展開 — 広告単価向上</li>
<li>通年売上・営業利益率ガイダンスを変更せず維持（H2 で利益率改善見込み）</li>
</ul>
<button class="risk-toggle" onclick="toggleRisk(this)"><span class="lbl">さらに5件を表示</span><span class="chev">▾</span></button>
</div>
<div class="risk-card">
<h4>Risk Factors</h4>
<ul class="risk-top">
<li>Q2 ガイダンス未達 — 営業利益率 -1.5pt 見通し、H1 コンテンツ償却増が重石</li>
<li>Reed Hastings 取締役退任 — ガバナンス移行への心理的影響（売り増幅）</li>
<li>EPS ビートの質 — $1.23 は一時違約金 $2.8B 依存、コアは $0.75 でインライン</li>
</ul>
<ul class="risk-more">
<li>UCAN QoQ -1.8% — 価格改定効果の一巡、米国消費鈍化リスク</li>
<li>競合激化 — Paramount-WBD合併後の Max 再編、Disney+ 値上げ、YouTube 台頭</li>
<li>EU DSA / AVMS / 各国コンテンツ投資義務 — 規制・運営コスト上昇</li>
<li>為替ボラティリティ — 国際売上比率 57% が USD 換算値を振らす</li>
<li>会員数非開示継続 — 市場はエンゲージメント指標に依存、情報非対称性</li>
</ul>
<button class="risk-toggle" onclick="toggleRisk(this)"><span class="lbl">さらに5件を表示</span><span class="chev">▾</span></button>
</div>
</div>
</div>
</section>

============================================================
sec-compare (23 lines)
============================================================
<section class="sec3" data-accordion="" id="sec-compare">
<div class="sec3-title">QoQ Compare <span class="jp">· 前回決算（Q4 2025）との比較</span></div>
<div class="sec3-body">
<table class="cmp-tbl">
<thead><tr><th>指標</th><th>Q4 2025</th><th>Q1 2026</th><th>変化</th></tr></thead>
<tbody>
<tr><td>売上高</td><td>$12.05B</td><td>$12.25B</td><td class="pos">+1.7% QoQ</td></tr>
<tr><td>EPS（Diluted, GAAP）</td><td>$0.56</td><td>$1.23</td><td class="pos">+119.6% QoQ ※違約金寄与</td></tr>
<tr><td>コアEPS（一時要因除く）</td><td>$0.56</td><td>~$0.75</td><td class="pos">+34% QoQ</td></tr>
<tr><td>営業利益率</td><td>24.5%</td><td>32.3%</td><td class="pos">+7.8pt Q4季節正常化</td></tr>
<tr><td>FCF</td><td>$1.87B</td><td>$5.09B</td><td class="pos">+$3.22B 違約金寄与大</td></tr>
<tr><td>自社株買い</td><td>$2.08B</td><td>$1.27B</td><td class="neu">継続</td></tr>
<tr><td>Q2 売上ガイダンス</td><td>—</td><td>$12.57B (-$70M vs コンセ)</td><td class="neg">ミス</td></tr>
<tr><td>通年 FCF ガイダンス</td><td>$11B</td><td>$12.5B</td><td class="pos">+$1.5B 上方修正</td></tr>
<tr><td>株価（発表翌日 / AH）</td><td>変動小</td><td>$107.79 → $98.17</td><td class="neg">-8.9%</td></tr>
<tr><td>総合評価スコア</td><td>—</td><td>3</td><td class="neu">一時要因除くとインライン</td></tr>
</tbody>
</table>
<div class="insight" style="margin-top:14px">
<div class="insight-body"><strong>トレンド方向: 横ばい → 一時要因で表面改善</strong> — 表面の売上・EPS・営業利益率は全て Q4 2025 より改善しましたが、これは<strong>Q4 が季節要因で低迷していた反動</strong>（コンテンツマーケ費用集中）と、<strong>WBD違約金 $2.8B の一時計上</strong>による嵩上げが主因。コア指標（一時要因除く）ベースでは前年比緩やかな成長の延長線上にあり、<strong>構造的なブレイクアウトとは言えません</strong>。また Q2 ガイダンスがコンセンサスを下回ったことで、前年 Q1→Q2 で伸びた営業利益率の軌道が今年は踏襲できない見通し。通年ガイダンス維持・FCF 上方修正は強みですが、市場は「ビートの質」を見抜き翌 AH で <strong>-8.9%</strong> と反応しました。</div>
</div>
</div>
</section>

============================================================
sec-geo (49 lines, showing first 35)
============================================================
<section class="sec3" data-accordion="" id="sec-geo">
<div class="sec3-title">Geography <span class="jp">· 地域別売上構成</span></div>
<div class="sec3-body">
<!-- Geography Donut (unified with insight) -->
<div class="panel-merge">
<div class="chart-split">
<div class="chart-split-viz"><canvas id="geoChart"></canvas></div>
<div class="chart-split-list">
<div class="chart-split-item">
<div class="csi-sw" style="background:#D4A843"></div>
<div>
<div class="csi-lbl">UCAN（米・加）</div>
<div class="csi-sub">$5.25B / YoY +13.6% / QoQ <span class="neg">-1.8%</span> 値上げ効果一巡</div>
</div>
<div class="csi-pct">42.8%</div>
</div>
<div class="chart-split-item">
<div class="csi-sw" style="background:#5C7395"></div>
<div>
<div class="csi-lbl">EMEA（欧州・中東・アフリカ）</div>
<div class="csi-sub">$4.00B / YoY +17.4% / FX中立 +12% / QoQ +3.2%</div>
</div>
<div class="csi-pct">32.6%</div>
</div>
<div class="chart-split-item">
<div class="csi-sw" style="background:#B8912A"></div>
<div>
<div class="csi-lbl">APAC（アジア太平洋）</div>
<div class="csi-sub">$1.51B / <strong>YoY +19.9%（首位）</strong> / 日本WBC寄与</div>
</div>
<div class="csi-pct">12.3%</div>
</div>
<div class="chart-split-item">
<div class="csi-sw" style="background:#F0E6C8"></div>
<div>
...

============================================================
sec-cashflow (37 lines)
============================================================
<section class="sec3" data-accordion="" id="sec-cashflow">
<div class="sec3-title">Cash Flow &amp; Content Spend <span class="jp">· キャッシュフロー・コンテンツ投資</span></div>
<div class="sec3-body">
<!-- 7Q キャッシュフロー推移チャート + 解説 一体化 -->
<div class="panel-merge">
<div class="chart-box" style="background:transparent;border:none;border-radius:0;padding:22px 24px 18px">
<div class="chart-wrap" style="height:320px"><canvas id="cashflowChart"></canvas></div>
</div>
<div class="panel-merge-divider"></div>
<div class="insight">
<div class="insight-body">Q1 2026 の営業CF は <strong>$5.29B（YoY +90%）</strong>、FCF は <strong>$5.09B（YoY +91%）</strong>と急増。主因は Paramount から受領した WBD解約違約金 <strong>$2.8B</strong> の現金計上。これを除いたコア営業CFは概ね $2.5B 前後で前年並み水準です。Netflix は違約金受領後ただちに<strong>自社株買いを再開</strong>し、Q1 に 1,350万株 / $1.27B を買い戻し（残り授権 $6.8B）。コンテンツ投資（cash content additions）は Q1 $4.85B、年間 ~$18B 水準。償却との比率は ~1.1倍。2026通年 FCF ガイダンスは $11B → <strong>$12.5B</strong> に上方修正。</div>
</div>
</div>
<div class="cardx-grid">
<div class="cardx">
<div class="cardx-lbl">Q1 営業CF</div>
<div class="cardx-val pos">$5.29B</div>
<div class="cardx-sub">YoY +89.7% / 違約金寄与 ~$2.8B</div>
</div>
<div class="cardx">
<div class="cardx-lbl">Q1 FCF</div>
<div class="cardx-val pos">$5.09B</div>
<div class="cardx-sub">YoY +91.4% / 通年ガイ <strong>$12.5B</strong> へ上方</div>
</div>
<div class="cardx">
<div class="cardx-lbl">Q1 自社株買い</div>
<div class="cardx-val gold">$1.27B</div>
<div class="cardx-sub">1,350万株 / 残り授権 $6.8B</div>
</div>
<div class="cardx">
<div class="cardx-lbl">現金残高 / ネットデット</div>
<div class="cardx-val neu">$12.26B / $2.1B</div>
<div class="cardx-sub">現金YoY +70% / 財務体質良好</div>
</div>
</div>
</div>
</section>

============================================================
sec-technical (97 lines, showing first 35)
============================================================
<section class="sec3" data-accordion="" id="sec-technical">
<div class="sec3-title">Technical <span class="jp">· テクニカル分析</span></div>
<div class="sec3-body">
<div class="cardx-grid">
<div class="cardx no-currency">
<div class="cardx-lbl">現在株価</div>
<div class="cardx-val neg">$98.17</div>
<div class="cardx-sub">決算後AH / 通常取引終値 $107.79 比 -8.92%</div>
</div>
<div class="cardx no-currency">
<div class="cardx-lbl">52週レンジ</div>
<div class="cardx-val neu">$75.01 – $134.12</div>
<div class="cardx-sub">2/23安値→6/30高値 / 中間域</div>
</div>
<div class="cardx">
<div class="cardx-lbl">時価総額</div>
<div class="cardx-val neu"><span class="no-currency">$422B</span></div>
<div class="cardx-sub">4,298M株 × $98.17（決算後AH水準）</div>
</div>
<div class="cardx">
<div class="cardx-lbl">RSI（14日）<span class="info" onclick="tipToggle(this)" tabindex="0"><svg aria-hidden="true" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" viewbox="0 0 16 16"><circle cx="8" cy="8" r="6.5"></circle><line x1="8" x2="8" y1="7.5" y2="11.5"></line><circle cx="8" cy="4.8" fill="currentColor" r=".65" stroke="none"></circle></svg></span><span class="tip-pop"><span class="tip-title">RSI（Relative Strength Index）</span><span class="tip-body">買われ過ぎ・売られ過ぎを示す指標。70超で「過熱」、30以下で「売られ過ぎ」の目安。決算前は 70〜85 の極度の過熱圏だったが、急落で中立圏へ。</span></span></div>
<div class="cardx-val neu">~50</div>
<div class="cardx-sub">決算前 70-85 過熱圏 → 急落で中立圏へ急低下</div>
</div>
<div class="cardx">
<div class="cardx-lbl">MACD</div>
<div class="cardx-val neg">ベア転換懸念</div>
<div class="cardx-sub">決算前ヒストグラム正 → 急落でゼロ近接</div>
</div>
<div class="cardx no-currency">
<div class="cardx-lbl">SMA 50日</div>
<div class="cardx-val neu">~$97 – $103</div>
<div class="cardx-sub">株価と交錯、攻防ライン</div>
</div>
<div class="cardx no-currency">
...

============================================================
sec-mgmt (25 lines)
============================================================
<section class="sec3" data-accordion="" id="sec-mgmt">
<div class="sec3-title">Management <span class="jp">· 経営陣コメント</span></div>
<div class="sec3-body">
<div class="pullq">
<div class="pullq-body">Q1 の <strong>社内品質エンゲージメント指標は過去最高</strong>に達した。Warner Bros. Discovery は我々の戦略を加速させる手段になり得たが、<strong>正しい価格でなければ意味がない</strong>。複数の成長経路（自社制作・ライセンス・パートナー）を持っており、コア事業への高い確信がある。</div>
<div class="pullq-attr">Ted Sarandos<span class="role">/ Co-CEO — WBD買収断念について</span></div>
</div>
<div class="pullq">
<div class="pullq-body">Q1 の視聴時間は 2025年後半と同程度の成長率で推移した。ウィンターオリンピック（ライバルコンテンツ）があったにもかかわらず。<strong>広告ビジネスは順調で、2026年の広告収入は前年比2倍の約 $3B</strong>を見込む。生成AI広告を2026年全AVOD市場に展開する。</div>
<div class="pullq-attr">Greg Peters<span class="role">/ Co-CEO — 広告事業について</span></div>
</div>
<div class="pullq">
<div class="pullq-body">Q1 の営業CF は <strong>$5.3B</strong> で、前年Q1の $2.8B から大幅増加。この増加は <strong>$2.8B の違約金現金受領が主因</strong>。これを受け <strong>2026通年FCFガイダンスを $11B → $12.5B に引き上げた</strong>。資本配分方針に変更はなく、違約金受領後ただちに自社株買いを再開した。</div>
<div class="pullq-attr">Spencer Neumann<span class="role">/ CFO — キャッシュフロー・ガイダンスについて</span></div>
</div>
<div class="pullq">
<div class="pullq-body">Q2 は 2026年内でコンテンツ償却の YoY 増加率が最も高い四半期となる見込み。H2（Q3 / Q4）では営業利益率の YoY 改善を見込み、<strong>通年 31.5% 目標は維持</strong>する。H1 の営業利益率プレッシャーは構造的なコンテンツ投資タイミングの問題であり、事業の収益性そのものの悪化ではない。</div>
<div class="pullq-attr">Spencer Neumann<span class="role">/ CFO — Q2/H2 見通し</span></div>
</div>
<div class="pullq">
<div class="pullq-body">リードは<strong>エコノミストでエンジニアでもあるが、心の中では教師</strong>だ。1999年に出会って以来、彼は私の最も大きな励みの源だった。リードはネットフリックスの創業者であり、最大の応援者として常に我々のDNAの一部だ。「Netflix は十分に強くなり、独立して舵取りできる段階に到達した」と彼自身が語った。</div>
<div class="pullq-attr">Co-CEO共同声明<span class="role">/ Reed Hastings 会長退任に寄せて</span></div>
</div>
</div>
</section>

============================================================
sec-valuation (50 lines, showing first 35)
============================================================
<section class="sec3" data-accordion="" id="sec-valuation">
<div class="sec3-title">Valuation <span class="jp">· 想定株価 3パターン</span></div>
<div class="sec3-body">
<div class="val-grid no-currency">
<div class="val-card">
<div class="val-scn">LOW — 保守的</div>
<div class="val-price">$75</div>
<div class="val-detail">Forward EPS $3.00（コアベース下限）<br/>× PER 25x（過去レンジ下限）</div>
<div class="val-gap neg">現在株価比 -23.6%</div>
</div>
<div class="val-card">
<div class="val-scn">MID — 基本</div>
<div class="val-price">$96</div>
<div class="val-detail">Forward EPS $3.20（コンセ水準）<br/>× PER 30x（過去3年平均）</div>
<div class="val-gap neu">現在株価比 -2.2%</div>
</div>
<div class="val-card">
<div class="val-scn">HIGH — 楽観的</div>
<div class="val-price">$119</div>
<div class="val-detail">Forward EPS $3.40（楽観）<br/>× PER 35x（過去レンジ上限）</div>
<div class="val-gap pos">現在株価比 +21.2%</div>
</div>
</div>
<!-- 補助メトリクス (Forward PER のみ) -->
<div class="cardx-grid" style="margin-top:18px;grid-template-columns:minmax(220px,340px)">
<div class="cardx"><div class="cardx-lbl">Forward PER（FY26E）<span class="info" onclick="tipToggle(this)" tabindex="0"><svg aria-hidden="true" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" viewbox="0 0 16 16"><circle cx="8" cy="8" r="6.5"></circle><line x1="8" x2="8" y1="7.5" y2="11.5"></line><circle cx="8" cy="4.8" fill="currentColor" r=".65" stroke="none"></circle></svg></span><span class="tip-pop"><span class="tip-title">Forward PER</span><span class="tip-body">株価を次期EPS予想で割った値。低いほど割安、高いほど割高の目安。成長企業は高めになりやすい。</span></span></div><div class="cardx-val neu">~31x</div><div class="cardx-sub">FY26E EPS $3.20（コアベース）</div></div>
</div>
<!-- 価格ポジション + 読み解き + 注意喚起 を一体化 -->
<div class="panel-merge no-currency" style="margin-top:18px">
<!-- G. Valuation Price-Position Gauge -->
<div class="val-gauge">
<div class="val-gauge-title">Price Position · 現在株価の位置</div>
<div class="val-gauge-track">
<div class="val-gauge-mark" style="left:0%"><div class="lbl">LOW</div><div class="amt">$75</div></div>
<div class="val-gauge-mark" style="left:47.7%"><div class="lbl">MID</div><div class="amt">$96</div></div>
...


============================================================
footer (2026-04-20 確定 / Atlas Quarterly 全レポート統一フォーマット)
============================================================
**配置**: `</body>` 直前（scripts の後）、`<footer class="footer">` タグで囲む。
**CSS**: `.footer{text-align:center;padding:40px 20px 24px;border-top:1px solid var(--border);margin-top:48px;color:var(--t3)}` / `.footer p{font-family:'Noto Serif JP',serif;font-size:.86rem;line-height:2;color:var(--t2);max-width:640px;margin:0 auto}` / `.footer .footer-id{margin-top:14px;font-family:'Inter',sans-serif;font-size:.72rem;color:var(--t3);letter-spacing:.05em}`

**必須3要素（順序厳守）**:
1. **Atlas Quarterlyロゴ画像**（テキスト見出しは廃止）
   - src: `https://atlas-financials.jp/reports/logos/atlas-quarterly-type-gold-transparent-300w.png`
   - style: `height:22px;width:auto;max-width:200px;opacity:.9;display:block;margin:0 auto 18px`
2. **免責本文**（定型文。`{TICKER名}` と `{会社名}` だけ差し替え）
3. **footer-id**（`{TICKER} / {Quarter} · 発行 YYYY-MM-DD · Atlas Quarterly — U.S. Market Intelligence`）

```html
<footer class="footer">
  <img src="https://atlas-financials.jp/reports/logos/atlas-quarterly-type-gold-transparent-300w.png" alt="Atlas Quarterly" style="height:22px;width:auto;max-width:200px;opacity:.9;display:block;margin:0 auto 18px">
  <p>本レポートは <strong>Atlas編集部</strong> が公開情報（{会社名} IR、プレスリリース、決算カンファレンスコール、各種金融メディア）に基づき作成した情報提供資料です。特定の有価証券の売買を推奨・勧誘するものではありません。投資判断は必ずご自身の責任で行ってください。数値・見通しは発表当時の情報に基づいており、将来の結果を保証するものではありません。</p>
  <div class="footer-id">{TICKER} / {Quarter} · 発行 2026-04-20 · Atlas Quarterly — U.S. Market Intelligence</div>
</footer>
```

**禁止**:
- 「ATLAS QUARTERLY」テキスト見出しの併記（ロゴ画像に一本化）
- 「Generated by Atlas Quarterly」等の英語クレジット文（`footer-id` 形式に統一）
- 免責文内での "Atlas Quarterly" 表記（常に **Atlas編集部** を使用）

**リファレンス実装**: `~/ui-kabu-reports/WFC/FY26Q1.html` L1321-1327 / `~/ui-kabu-reports/JNJ/FY26Q1.html`


============================================================
数値の通貨切替対応（2026-04-20 追記）
============================================================
currency-toggle の正規表現 `/\$(\d+(?:,\d{3})*(?:\.\d+)?)\s*([TBMK])?(?![\w%])/g` は **`$` を起点**に検出する。

**必須ルール**: 範囲表記（A〜B / A-B）は**両端に `$` と単位を明記**すること。

| ❌ NG | ✅ OK |
|---|---|
| `$100.3-101.3B` | `$100.3B-$101.3B` |
| `$100.3〜101.3B` | `$100.3B〜$101.3B` |
| `$100,300-101,300M` | `$100,300M-$101,300M` |
| `$11.45-11.65` | `$11.45-$11.65` |

**理由**: 右端に `$` が無いと正規表現が左値のみマッチ → 通貨トグル時に「左端だけJPY換算・右端はUSDのまま」の不整合表示となる。

**自動QCコマンド**:
```bash
grep -nE '\$[0-9,]+(\.\d+)?[-〜～][0-9,]+(\.\d+)?[BMTK]?' {FILE}.html
# マッチ0件が正常
```

