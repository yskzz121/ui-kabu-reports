#!/usr/bin/env python3
"""
deploy_report.py
================
決算レポートHTMLをGitHub Pagesに自動デプロイし、
LINE U&I株倶楽部グループに自動通知するスクリプト。

使い方:
  python3 deploy_report.py <HTMLファイルパス> <ティッカー> <四半期> [評価スコア] [コメント]

例:
  python3 deploy_report.py ~/投資分析/銘柄分析/NVDA/NVDA_FY26Q4.html NVDA FY26Q4
  python3 deploy_report.py ~/投資分析/銘柄分析/NVDA/NVDA_FY26Q4.html NVDA FY26Q4 5 "売上・EPSともにビート！ガイダンスも上方修正"
"""

import sys, os, shutil, subprocess, json
from datetime import datetime
try:
    import urllib.request as urlreq
    import urllib.error
except ImportError:
    pass

GITHUB_USERNAME = "yskzz121"
REPO_NAME       = "ui-kabu-reports"
REPO_DIR        = os.path.expanduser("~/ui-kabu-reports")
PAGES_BASE_URL  = f"https://{GITHUB_USERNAME}.github.io/{REPO_NAME}"
LINE_CONFIG     = os.path.expanduser("~/.line_config")

SCORE_LABELS = {
    "5": "5🚀 素晴らしい決算",
    "4": "4📈 良い決算",
    "3": "3⏸️ 悪くない決算",
    "2": "2📉 悪い決算",
    "1": "1👎 壊滅的な決算",
}

SECTOR_MAP = {
    "ADI":   "半導体・アナログ/混合信号",
    "ALAB":  "半導体・AIインフラ",
    "AMZN":  "EC・クラウド・広告",
    "AVGO":  "半導体・インフラSW",
    "CIEN":  "光ネットワーキング",
    "COST":  "小売・会員制倉庫",
    "DDOG":  "SaaS・オブザーバビリティ",
    "FN":    "精密光学・電子機器製造",
    "GOOGL": "テクノロジー・広告",
    "IOT":   "SaaS・IoT",
    "LLY":   "ヘルスケア・医薬品",
    "MRVL":  "半導体・AIインフラ",
    "MSFT":  "クラウド・ソフトウェア・AI",
    "MU":    "半導体・メモリ",
    "NVDA":  "半導体・GPU",
    "OKTA":  "SaaS・ID管理",
    "ORCL":  "エンタープライズSW・クラウド",
    "PANW":  "サイバーセキュリティ",
    "PATH":  "エンタープライズSW・RPA",
    "RBRK":  "サイバーセキュリティ・データ保護",
    "RDDT":  "ソーシャルメディア",
    "SNAP":  "ソーシャルメディア",
    "TSLA":  "EV・エネルギー",
    "TXN":   "半導体・アナログ",
    "ZS":    "サイバーセキュリティ",
}

# ─────────────────────────────────────────
def run(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, cwd=cwd or REPO_DIR,
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"コマンド失敗: {cmd}\n{result.stderr}")
    return result.stdout.strip()

def load_line_config():
    config = {}
    if not os.path.exists(LINE_CONFIG):
        return config
    with open(LINE_CONFIG) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                config[k.strip()] = v.strip()
    return config

def send_line(token, group_id, message, max_retries=3):
    import time
    data = json.dumps({
        "to": group_id,
        "messages": [{"type": "text", "text": message}]
    }).encode("utf-8")
    for attempt in range(1, max_retries + 1):
        req = urlreq.Request(
            "https://api.line.me/v2/bot/message/push",
            data=data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        try:
            with urlreq.urlopen(req, timeout=10) as res:
                return res.status == 200
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < max_retries:
                wait = int(e.headers.get("Retry-After", 5 * attempt))
                print(f"  ⏳ レート制限（429）。{wait}秒後にリトライ ({attempt}/{max_retries})...")
                time.sleep(wait)
            else:
                print(f"⚠️  LINE送信エラー: {e}")
                return False
        except Exception as e:
            print(f"⚠️  LINE送信エラー: {e}")
            return False
    return False

def make_ticker_index(ticker, reports):
    latest_file, latest_quarter = reports[0][1], reports[0][0]
    archive_rows = ""
    for quarter, filename in reports[1:]:
        url = f"{PAGES_BASE_URL}/{ticker}/{filename}"
        archive_rows += f'<li><a href="{url}">{quarter}</a></li>\n'
    return f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8">
<meta http-equiv="refresh" content="0; url=./{latest_file}">
<title>{ticker} - U&I株倶楽部</title>
<style>body{{font-family:sans-serif;background:#0f1117;color:#e0e0e0;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}}.card{{background:#1a1d27;border-radius:12px;padding:40px;max-width:500px;width:100%;text-align:center}}h1{{color:#60a5fa}}.btn{{display:inline-block;background:#3b82f6;color:white;padding:12px 28px;border-radius:8px;text-decoration:none;font-weight:bold;margin-top:16px}}.archive{{margin-top:24px;text-align:left}}.archive a{{color:#93c5fd}}</style>
</head><body><div class="card"><h1>{ticker}</h1><p>最新レポートに移動中...</p>
<a class="btn" href="./{latest_file}">📊 {latest_quarter} を見る</a>
{"<div class='archive'><h3>過去のレポート</h3><ul>" + archive_rows + "</ul></div>" if archive_rows else ""}
</div></body></html>"""

def _parse_fy_quarter(name):
    """ファイル名からFY年度とクォーターを抽出。例: FY26Q1 → ('FY26','Q1'), FY2025Q4 → ('FY2025','Q4')"""
    import re
    m = re.match(r'(FY\d+)(Q\d)', name)
    if m:
        return m.group(1), m.group(2)
    # MU_Q1_FY2026 のような特殊パターン
    m = re.match(r'.*_(Q\d)_(FY\d+)', name)
    if m:
        return m.group(2), m.group(1)
    return None, None

def make_root_index(ticker_data):
    cards = ""
    for ticker in sorted(ticker_data.keys()):
        reports = ticker_data[ticker]
        sector = SECTOR_MAP.get(ticker, "")
        latest_q, latest_f = reports[0]

        # FY年度ごとにクォーターをグループ化
        fy_groups = {}
        for qname, fname in reports:
            fy, q = _parse_fy_quarter(qname)
            if fy and q:
                fy_groups.setdefault(fy, []).append((q, fname))
            else:
                fy_groups.setdefault("その他", []).append((qname, fname))

        # FY年度を降順ソート
        fy_html = ""
        for fy in sorted(fy_groups.keys(), reverse=True):
            quarters = fy_groups[fy]
            # クォーターを昇順ソート
            quarters.sort(key=lambda x: x[0])
            pills = ""
            for q, fname in quarters:
                url = f"{PAGES_BASE_URL}/{ticker}/{fname}"
                pills += f'<a class="q-pill" href="{url}">{q}</a>'
            fy_html += f'<div class="fy-row"><span class="fy-label">{fy}</span><div class="q-pills">{pills}</div></div>'

        sector_html = f'<div class="sector">{sector}</div>' if sector else ''
        logo_file = f"logos/{ticker}.svg"
        logo_html = f'<img class="card-logo" src="{logo_file}" alt="{ticker}">' if os.path.exists(os.path.join(REPO_DIR, logo_file)) else ''
        cards += f'<div class="card" data-ticker="{ticker}" data-sector="{sector}"><div class="card-header"><div class="ticker">{ticker}</div>{sector_html}{logo_html}</div>{fy_html}</div>'

    now = datetime.now().strftime("%Y/%m/%d %H:%M")
    return f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>U&I株倶楽部 決算レポート</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Noto Sans JP',sans-serif;background:#0d1117;color:#e6edf3;padding:40px 20px}}
header{{text-align:center;margin-bottom:48px}}
header h1{{color:#58a6ff;font-size:1.8rem;font-weight:700}}
header p{{color:#6e7681;font-size:.85rem;margin-top:8px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px;max-width:1100px;margin:0 auto}}
.card{{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:24px;display:flex;flex-direction:column;gap:14px;transition:border-color .2s}}
.card:hover{{border-color:#58a6ff}}
.card-header{{display:flex;align-items:baseline;gap:12px}}
.ticker{{font-size:1.5rem;font-weight:700;color:#e6edf3}}
.sector{{font-size:.75rem;color:#8b949e;background:rgba(88,166,255,.1);padding:2px 10px;border-radius:12px;white-space:nowrap}}
.fy-row{{display:flex;align-items:center;gap:10px;margin-bottom:6px}}
.fy-label{{font-size:.8rem;font-weight:700;color:#8b949e;min-width:52px}}
.q-pills{{display:flex;gap:6px;flex-wrap:wrap}}
.q-pill{{font-size:.78rem;font-weight:500;padding:4px 14px;border-radius:8px;background:#21262d;color:#58a6ff;text-decoration:none;border:1px solid #30363d;transition:all .15s}}
.q-pill:hover{{background:#58a6ff;color:#0d1117;border-color:#58a6ff}}
footer{{text-align:center;margin-top:48px;color:#30363d;font-size:.75rem}}
.sort-bar{{text-align:center;margin-bottom:24px}}
.sort-btn{{font-family:'Noto Sans JP',sans-serif;font-size:.82rem;font-weight:500;padding:6px 18px;margin:0 4px;border-radius:8px;border:1px solid #30363d;background:#161b22;color:#8b949e;cursor:pointer;transition:all .15s}}
.sort-btn.active{{background:#58a6ff;color:#0d1117;border-color:#58a6ff}}
.sort-btn:hover:not(.active){{border-color:#58a6ff;color:#58a6ff}}
.sector-heading{{color:#58a6ff;font-size:1rem;font-weight:700;margin:28px 0 12px;padding-bottom:8px;border-bottom:1px solid #21262d;grid-column:1/-1}}
</style>
</head><body>
<header><h1>📊 U&I株倶楽部 決算レポート</h1><p>最終更新: {now}</p></header>
<div class="sort-bar"><button class="sort-btn active" onclick="sortBy('ticker')">ABC順</button><button class="sort-btn" onclick="sortBy('sector')">セクター別</button></div>
<div class="grid" id="grid">{cards}</div>
<footer>U&I株倶楽部 · Powered by Claude</footer>
<script>
function sortBy(mode){{
  var grid=document.getElementById('grid');
  var btns=document.querySelectorAll('.sort-btn');
  btns.forEach(function(b){{b.classList.remove('active')}});
  event.target.classList.add('active');
  // Remove sector headings
  grid.querySelectorAll('.sector-heading').forEach(function(h){{h.remove()}});
  var cards=Array.from(grid.querySelectorAll('.card'));
  if(mode==='ticker'){{
    cards.sort(function(a,b){{return a.dataset.ticker.localeCompare(b.dataset.ticker)}});
    cards.forEach(function(c){{grid.appendChild(c)}});
  }}else{{
    cards.sort(function(a,b){{
      var s=a.dataset.sector.localeCompare(b.dataset.sector);
      return s!==0?s:a.dataset.ticker.localeCompare(b.dataset.ticker);
    }});
    var last='';
    cards.forEach(function(c){{
      if(c.dataset.sector!==last){{
        last=c.dataset.sector;
        var h=document.createElement('div');
        h.className='sector-heading';
        h.textContent=last||'その他';
        grid.appendChild(h);
      }}
      grid.appendChild(c);
    }});
  }}
}}
</script>
</body></html>"""

def scan_existing_reports(ticker):
    ticker_dir = os.path.join(REPO_DIR, ticker)
    if not os.path.exists(ticker_dir):
        return []
    files = sorted([f for f in os.listdir(ticker_dir)
                    if f.endswith(".html") and f != "index.html"], reverse=True)
    return [(os.path.splitext(f)[0], f) for f in files]

def scan_all_tickers():
    result = {}
    for item in os.listdir(REPO_DIR):
        full = os.path.join(REPO_DIR, item)
        if os.path.isdir(full) and not item.startswith("."):
            reports = scan_existing_reports(item)
            if reports:
                result[item] = reports
    return result

def deploy(html_path, ticker, quarter, score=None, comment=None):
    ticker    = ticker.upper()
    html_path = os.path.expanduser(html_path)

    if not os.path.exists(html_path):
        raise FileNotFoundError(f"HTMLファイルが見つかりません: {html_path}")

    filename   = f"{quarter}.html"
    ticker_dir = os.path.join(REPO_DIR, ticker)
    dest_path  = os.path.join(ticker_dir, filename)

    print(f"\n🚀 デプロイ開始: {ticker} {quarter}")

    # ── 1. 最新化
    print("📥 リポジトリを最新化中...")
    run("git pull origin main")

    # ── 2. HTMLコピー
    os.makedirs(ticker_dir, exist_ok=True)
    shutil.copy2(html_path, dest_path)
    print(f"✅ HTMLコピー: {ticker}/{filename}")

    # ── 3. 銘柄index更新
    reports = scan_existing_reports(ticker)
    with open(os.path.join(ticker_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(make_ticker_index(ticker, reports))
    print(f"✅ {ticker}/index.html 更新")

    # ── 4. ルートindex更新
    with open(os.path.join(REPO_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(make_root_index(scan_all_tickers()))
    print("✅ 全銘柄ポータル更新")

    # ── 5. push
    print("📤 GitHubにプッシュ中...")
    run("git add -A")
    run(f'git commit -m "Add {ticker} {quarter} report"')
    run("git push origin main")
    print("✅ プッシュ完了")

    report_url = f"{PAGES_BASE_URL}/{ticker}/{filename}"
    portal_url = f"{PAGES_BASE_URL}/"

    # ── 6. LINE送信
    line_cfg = load_line_config()
    line_token    = line_cfg.get("LINE_TOKEN", "")
    line_group_id = line_cfg.get("LINE_GROUP_ID", "")

    line_sent = False
    if line_token and line_group_id and not line_token.startswith("ここに"):
        score_label = SCORE_LABELS.get(str(score), "") if score else ""
        now_str     = datetime.now().strftime("%Y/%m/%d %H:%M")

        msg_lines = [
            f"📊 【{ticker} {quarter} 決算レポート】",
        ]
        if score_label:
            msg_lines.append(f"総合評価: {score_label}")
        if comment:
            msg_lines.append(f"💬 {comment}")
        msg_lines += [
            f"",
            f"🔗 レポートはこちら:",
            f"{report_url}",
            f"",
            f"🏠 全銘柄ポータル:",
            f"{portal_url}",
            f"",
            f"({now_str} 自動配信)",
        ]
        message = "\n".join(msg_lines)

        print("\n📱 LINEグループに送信中...")
        line_sent = send_line(line_token, line_group_id, message)
        if line_sent:
            print("✅ LINE送信完了！")
        else:
            print("⚠️  LINE送信失敗（デプロイは完了しています）")
    else:
        print("⚠️  LINE設定が未完了のためスキップ")

    # ── 7. 完了表示
    print(f"""
{'='*55}
🎉 デプロイ完了！

📊 LINEに貼るURL:
   {report_url}

🏠 全銘柄ポータル:
   {portal_url}

📱 LINE自動送信: {"✅ 送信済み" if line_sent else "⚠️ 未送信"}
{'='*55}
""")
    return report_url

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("使い方: python3 deploy_report.py <HTMLパス> <TICKER> <QUARTER> [スコア1-5] [コメント]")
        print("例    : python3 deploy_report.py ~/投資分析/銘柄分析/NVDA/NVDA_FY26Q4.html NVDA FY26Q4 5 '売上・EPSともにビート'")
        sys.exit(1)

    html_path = sys.argv[1]
    ticker    = sys.argv[2]
    quarter   = sys.argv[3]
    score     = sys.argv[4] if len(sys.argv) > 4 else None
    comment   = sys.argv[5] if len(sys.argv) > 5 else None

    try:
        deploy(html_path, ticker, quarter, score, comment)
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        sys.exit(1)
