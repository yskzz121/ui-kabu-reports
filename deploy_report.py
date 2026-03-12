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

SCORE_ICONS = {5: "🚀", 4: "📈", 3: "⏸️", 2: "📉", 1: "👎"}

def extract_score_from_report(ticker):
    """レポートHTMLからスコアを抽出（最新レポートの複数パターンを探す）"""
    import re
    ticker_dir = os.path.join(REPO_DIR, ticker)
    if not os.path.isdir(ticker_dir):
        return None
    htmls = sorted([f for f in os.listdir(ticker_dir) if f.endswith(".html") and f != "index.html"], reverse=True)
    if not htmls:
        return None
    path = os.path.join(ticker_dir, htmls[0])
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read(30000)
        patterns = [
            r'class="score-number[^"]*"[^>]*>\s*(\d)',
            r'class="score-num"[^>]*>\s*(\d)',
            r'class="score-label"[^>]*>\s*(\d)\s*[／/]\s*5',
            r'スコア\s*(\d)\s*[／/]\s*5',
            r'score-badge[^>]*>\s*<span[^>]*>\s*(\d)',
        ]
        for pat in patterns:
            m = re.search(pat, content)
            if m:
                return int(m.group(1))
        # Fallback: count score-dot active elements
        dots = len(re.findall(r'class="score-dot active"', content))
        if 1 <= dots <= 5:
            return dots
    except Exception:
        pass
    return None

SECTOR_MAP = {
    "ADI":   "半導体",
    "ALAB":  "半導体",
    "AMZN":  "テクノロジー",
    "AVGO":  "半導体",
    "CIEN":  "ネットワーク・光学",
    "COST":  "小売",
    "DDOG":  "SaaS・ソフトウェア",
    "FN":    "ネットワーク・光学",
    "GOOGL": "テクノロジー",
    "IOT":   "SaaS・ソフトウェア",
    "LLY":   "ヘルスケア",
    "MRVL":  "半導体",
    "MSFT":  "テクノロジー",
    "MU":    "半導体",
    "NVDA":  "半導体",
    "OKTA":  "SaaS・ソフトウェア",
    "ORCL":  "テクノロジー",
    "PANW":  "サイバーセキュリティ",
    "PATH":  "SaaS・ソフトウェア",
    "RBRK":  "サイバーセキュリティ",
    "RDDT":  "ソーシャルメディア",
    "SNAP":  "ソーシャルメディア",
    "TSLA":  "EV・エネルギー",
    "TXN":   "半導体",
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

def _normalize_fy(fy_str):
    """FY26 → FY2026, FY2025 → FY2025（4桁に統一）"""
    import re
    m = re.match(r'FY(\d+)', fy_str)
    if m:
        y = m.group(1)
        if len(y) == 2:
            return f"FY20{y}"
    return fy_str

def _parse_fy_quarter(name):
    """ファイル名からFY年度とクォーターを抽出し、FY表記を4桁に統一"""
    import re
    m = re.match(r'(FY\d+)(Q\d)', name)
    if m:
        return _normalize_fy(m.group(1)), m.group(2)
    # MU_Q1_FY2026 のような特殊パターン
    m = re.match(r'.*_(Q\d)_(FY\d+)', name)
    if m:
        return _normalize_fy(m.group(2)), m.group(1)
    return None, None

def _get_report_date(ticker, fname):
    """レポートファイルのgitコミット日を取得（YYYY-MM-DD文字列）。取得不可時はファイル更新日"""
    import re
    fpath = os.path.join(REPO_DIR, ticker, fname)
    try:
        result = subprocess.run(
            f'git log -1 --format="%ai" -- "{ticker}/{fname}"',
            shell=True, cwd=REPO_DIR, capture_output=True, text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()[:10]
    except Exception:
        pass
    try:
        mtime = os.path.getmtime(fpath)
        return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
    except Exception:
        return None

def make_root_index(ticker_data):
    from datetime import timedelta
    import re as _re
    three_weeks_ago = (datetime.now() - timedelta(weeks=3)).strftime("%Y-%m-%d")

    cards = ""
    for ticker in sorted(ticker_data.keys()):
        reports = ticker_data[ticker]
        sector = SECTOR_MAP.get(ticker, "")
        latest_q, latest_f = reports[0]

        # 最新レポートの日付を取得してNEW判定
        latest_date = _get_report_date(ticker, latest_f)
        is_new = latest_date and latest_date >= three_weeks_ago

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
            quarters.sort(key=lambda x: x[0])
            pills = ""
            for q, fname in quarters:
                url = f"{PAGES_BASE_URL}/{ticker}/{fname}"
                pills += f'<a class="q-pill" href="{url}">{q}</a>'
            fy_html += f'<div class="fy-row"><span class="fy-label">{fy}</span><div class="q-pills">{pills}</div></div>'

        sector_html = f'<div class="sector">{sector}</div>' if sector else ''
        new_html = '<span class="new-badge">NEW</span>' if is_new else ''
        logo_file = None
        for ext in ("svg", "png"):
            candidate = f"logos/{ticker}.{ext}"
            if os.path.exists(os.path.join(REPO_DIR, candidate)):
                logo_file = candidate
                break
        logo_html = f'<img class="card-logo" src="{logo_file}" alt="{ticker}">' if logo_file else ''

        # スコアバッジ
        score = extract_score_from_report(ticker)
        score_attr = f' data-score="{score}"' if score else ''
        score_html = ''
        if score:
            icon = SCORE_ICONS.get(score, "")
            if score >= 4:
                bg, fg, bd = "#2ea04322", "#2ea043", "#2ea04344"
            elif score == 3:
                bg, fg, bd = "#d2992222", "#d29922", "#d2992244"
            else:
                bg, fg, bd = "#f8514922", "#f85149", "#f8514944"
            score_html = f'<span class="score-badge" style="background:{bg};color:{fg};border:1px solid {bd}">{icon} {score}/5</span>'

        cards += (
            f'<div class="card" data-ticker="{ticker}"{score_attr} data-sector="{sector}">'
            f'<div class="card-top"><div class="card-id">{logo_html}<span class="ticker">{ticker}</span></div>'
            f'<div class="card-badges">{new_html}{score_html}</div></div>'
            f'{sector_html}'
            f'{fy_html}'
            f'</div>'
        )

    now = datetime.now().strftime("%Y/%m/%d %H:%M")
    return f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>U&I株倶楽部 決算レポート</title>
<meta name="description" content="U&I株倶楽部の米国株決算分析レポートポータル。四半期決算をインフォグラフィックで分かりやすく解説。">
<meta property="og:title" content="U&I株倶楽部 決算レポート">
<meta property="og:description" content="米国株の四半期決算をインフォグラフィックで分かりやすく分析。セクター別・スコア別に閲覧可能。">
<meta property="og:type" content="website">
<meta property="og:url" content="{PAGES_BASE_URL}/">
<meta property="og:image" content="{PAGES_BASE_URL}/apple-touch-icon.png">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary">
<link rel="icon" type="image/png" href="favicon.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Noto Sans JP',sans-serif;background:#0d1117;color:#e6edf3;padding:40px 20px}}
header{{text-align:center;margin-bottom:48px}}
header h1{{color:#58a6ff;font-size:1.8rem;font-weight:700;display:flex;align-items:center;justify-content:center;gap:14px}}
header h1 img{{height:44px;width:auto}}
header p{{color:#6e7681;font-size:.85rem;margin-top:8px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px;max-width:1100px;margin:0 auto}}
.card{{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:20px;display:flex;flex-direction:column;gap:10px;transition:border-color .2s}}
.card:hover{{border-color:#58a6ff}}
.card-top{{display:flex;align-items:center;justify-content:space-between;gap:10px}}
.card-id{{display:flex;align-items:center;gap:10px;min-width:0}}
.card-badges{{display:flex;align-items:center;gap:6px;flex-shrink:0}}
.card-logo{{height:26px;width:auto;max-width:40px;object-fit:contain;opacity:.85;flex-shrink:0}}
.card-logo[src$=".png"]{{border-radius:4px}}
.ticker{{font-size:1.4rem;font-weight:700;color:#e6edf3;white-space:nowrap}}
.sector{{font-size:.7rem;color:#8b949e;background:rgba(88,166,255,.08);padding:3px 10px;border-radius:10px;white-space:nowrap;display:inline-block;align-self:flex-start}}
.fy-row{{display:flex;align-items:center;gap:10px}}
.fy-label{{font-size:.78rem;font-weight:700;color:#6e7681;min-width:56px;flex-shrink:0}}
.q-pills{{display:flex;gap:6px;flex-wrap:wrap}}
.q-pill{{font-size:.76rem;font-weight:500;padding:4px 14px;border-radius:8px;background:#21262d;color:#58a6ff;text-decoration:none;border:1px solid #30363d;transition:all .15s}}
.q-pill:hover{{background:#58a6ff;color:#0d1117;border-color:#58a6ff}}
.sort-bar{{text-align:center;margin-bottom:24px}}
.sort-btn{{font-family:'Noto Sans JP',sans-serif;font-size:.82rem;font-weight:500;padding:6px 18px;margin:0 4px;border-radius:8px;border:1px solid #30363d;background:#161b22;color:#8b949e;cursor:pointer;transition:all .15s}}
.sort-btn.active{{background:#58a6ff;color:#0d1117;border-color:#58a6ff}}
.sort-btn:hover:not(.active){{border-color:#58a6ff;color:#58a6ff}}
.sector-heading{{color:#58a6ff;font-size:1rem;font-weight:700;margin:28px 0 12px;padding-bottom:8px;border-bottom:1px solid #21262d;grid-column:1/-1}}
.score-badge{{font-size:.68rem;font-weight:700;padding:2px 8px;border-radius:10px;white-space:nowrap;line-height:1.4}}
.new-badge{{font-size:.6rem;font-weight:700;padding:2px 7px;border-radius:10px;background:#da3633;color:#fff;white-space:nowrap;letter-spacing:.5px;animation:pulse 2s ease-in-out infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.6}}}}
.search-bar{{max-width:400px;margin:0 auto 20px;position:relative}}
.search-bar input{{width:100%;padding:10px 16px 10px 40px;border-radius:10px;border:1px solid #30363d;background:#161b22;color:#e6edf3;font-family:'Noto Sans JP',sans-serif;font-size:.9rem;outline:none;transition:border-color .15s}}
.search-bar input:focus{{border-color:#58a6ff}}
.search-bar svg{{position:absolute;left:12px;top:50%;transform:translateY(-50%);color:#6e7681}}
.card.hidden{{display:none}}
.no-results{{grid-column:1/-1;text-align:center;color:#6e7681;font-size:.9rem;padding:40px 0}}
footer{{text-align:center;margin-top:60px;padding:24px 20px;border-top:1px solid #21262d;color:#484f58;font-size:.75rem;line-height:1.8}}
footer a{{color:#58a6ff;text-decoration:none}}
footer a:hover{{text-decoration:underline}}
.scroll-top{{position:fixed;bottom:28px;right:28px;width:44px;height:44px;border-radius:50%;background:#161b22;border:1px solid #30363d;color:#58a6ff;font-size:1.2rem;cursor:pointer;display:flex;align-items:center;justify-content:center;opacity:0;visibility:hidden;transition:all .25s;z-index:100;box-shadow:0 2px 8px rgba(0,0,0,.3)}}
.scroll-top.visible{{opacity:1;visibility:visible}}
.scroll-top:hover{{background:#58a6ff;color:#0d1117;border-color:#58a6ff}}
</style>
</head><body>
<header><h1><img src="logos/ui-kabu-logo.png" alt="U&I">株倶楽部 決算レポート</h1><p>最終更新: {now}</p></header>
<div class="sort-bar"><button class="sort-btn active" onclick="sortBy('ticker')">ABC順</button><button class="sort-btn" onclick="sortBy('sector')">セクター別</button><button class="sort-btn" onclick="sortBy('score')">スコア順</button></div>
<div class="search-bar"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg><input type="text" id="search" placeholder="ティッカーで検索..." oninput="filterCards()"></div>
<div class="grid" id="grid">{cards}</div>
<footer>
<p>U&I株倶楽部 · Powered by <a href="https://claude.ai" target="_blank" rel="noopener">Claude</a></p>
<p style="margin-top:6px;font-size:.7rem;color:#30363d">本レポートは情報提供を目的としたものであり、特定の銘柄の売買を推奨するものではありません。投資判断はご自身の責任でお願いいたします。</p>
</footer>
<button class="scroll-top" id="scrollTop" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">&#9650;</button>
<script>
function sortBy(mode){{
  var grid=document.getElementById('grid');
  var btns=document.querySelectorAll('.sort-btn');
  btns.forEach(function(b){{b.classList.remove('active')}});
  event.target.classList.add('active');
  grid.querySelectorAll('.sector-heading').forEach(function(h){{h.remove()}});
  var cards=Array.from(grid.querySelectorAll('.card'));
  if(mode==='ticker'){{
    cards.sort(function(a,b){{return a.dataset.ticker.localeCompare(b.dataset.ticker)}});
    cards.forEach(function(c){{grid.appendChild(c)}});
  }}else if(mode==='score'){{
    cards.sort(function(a,b){{
      var s=parseInt(b.dataset.score||0)-parseInt(a.dataset.score||0);
      return s!==0?s:a.dataset.ticker.localeCompare(b.dataset.ticker);
    }});
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
function filterCards(){{
  var q=document.getElementById('search').value.toUpperCase();
  var grid=document.getElementById('grid');
  var cards=grid.querySelectorAll('.card');
  var found=0;
  cards.forEach(function(c){{
    var match=c.dataset.ticker.toUpperCase().indexOf(q)!==-1;
    c.classList.toggle('hidden',!match);
    if(match)found++;
  }});
  var nr=grid.querySelector('.no-results');
  if(found===0&&q){{
    if(!nr){{nr=document.createElement('div');nr.className='no-results';grid.appendChild(nr);}}
    nr.textContent='該当する銘柄が見つかりません';
  }}else if(nr){{nr.remove();}}
}}
window.addEventListener('scroll',function(){{
  var btn=document.getElementById('scrollTop');
  if(window.scrollY>300){{btn.classList.add('visible')}}else{{btn.classList.remove('visible')}}
}});
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
