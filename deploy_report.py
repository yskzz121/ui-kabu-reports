#!/usr/bin/env python3
"""
deploy_report.py
================
決算レポートHTMLをCloudflare Pagesに自動デプロイし、
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

REPO_DIR        = os.path.expanduser("~/ui-kabu-reports")
PAGES_BASE_URL  = "https://atlas-financials.jp/reports"
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
            r'class="score-big[^"]*"[^>]*>\s*(\d)',
            r'class="score-number[^"]*"[^>]*>\s*(\d)',
            r'class="score-num"[^>]*>\s*(\d)',
            r'class="score-label"[^>]*>\s*(\d)\s*[／/]\s*5',
            r'スコア\s*(\d)\s*[／/]\s*5',
            r'score-badge[^>]*>\s*<span[^>]*>\s*(\d)',
            r'score-badge[^>]*>(?:[^<]*?)(\d)\s*/\s*5',
        ]
        for pat in patterns:
            m = re.search(pat, content)
            if m:
                return int(m.group(1))
        # Fallback 1: emoji-based score detection
        emoji_map = {'🚀': 5, '📈': 4, '⏸️': 3, '📉': 2, '👎': 1}
        for emoji, sc in emoji_map.items():
            if emoji in content:
                return sc
        # Fallback 2: count score-dot active elements
        dots = len(re.findall(r'class="score-dot active"', content))
        if 1 <= dots <= 5:
            return dots
    except Exception:
        pass
    return None

def extract_sector_from_report(ticker):
    """レポートHTMLからセクター情報を自動抽出（SECTOR_MAPのフォールバック）"""
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
            content = f.read(50000)
        # パターン: セクター/業種/業界の表記を探す
        patterns = [
            r'セクター[：:]\s*([^\s<,、]+)',
            r'業種[：:]\s*([^\s<,、]+)',
            r'sector["\s:]+([^"<,]+)',
            r'data-sector="([^"]+)"',
        ]
        for pat in patterns:
            m = re.search(pat, content, re.IGNORECASE)
            if m:
                val = m.group(1).strip()
                if val and val != "—":
                    return val
    except Exception:
        pass
    return None

SECTOR_MAP = {
    "ACN":   "ITサービス",
    "ADBE":  "SaaS・ソフトウェア",
    "ADI":   "半導体",
    "ALAB":  "半導体",
    "AMZN":  "テクノロジー",
    "AVGO":  "半導体",
    "ASML":  "半導体",
    "BAC":   "金融",
    "BABA":  "テクノロジー",
    "BLK":   "金融",
    "C":     "金融",
    "MS":    "金融",
    "CIEN":  "ネットワーク・光学",
    "COST":  "小売",
    "DAL":   "航空・運輸",
    "DDOG":  "SaaS・ソフトウェア",
    "DG":    "小売",
    "DOCU":  "SaaS・ソフトウェア",
    "FDX":   "航空・運輸",
    "FN":    "ネットワーク・光学",
    "GOOGL": "テクノロジー",
    "IOT":   "SaaS・ソフトウェア",
    "JNJ":   "ヘルスケア",
    "JPM":   "金融",
    "GS":    "金融",
    "LLY":   "ヘルスケア",
    "LULU":  "アパレル・小売",
    "META":  "テクノロジー",
    "MRVL":  "半導体",
    "MSFT":  "テクノロジー",
    "MU":    "半導体",
    "NFLX":  "メディア・ストリーミング",
    "NKE":   "アパレル・小売",
    "NVDA":  "半導体",
    "OKTA":  "SaaS・ソフトウェア",
    "ORCL":  "テクノロジー",
    "PANW":  "サイバーセキュリティ",
    "PATH":  "SaaS・ソフトウェア",
    "PAYP":  "フィンテック",
    "PEP":   "食品・飲料",
    "RBRK":  "サイバーセキュリティ",
    "RDDT":  "ソーシャルメディア",
    "S":     "サイバーセキュリティ",
    "SMCI":  "サーバー・インフラ",
    "SNAP":  "ソーシャルメディア",
    "TM":    "自動車",
    "TSLA":  "EV・エネルギー",
    "TSM":   "半導体",
    "TXN":   "半導体",
    "VFC":   "アパレル・小売",
    "WFC":   "金融",
    "WMT":   "小売",
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
    """レポートファイルの初回追加日（公開日）を取得（YYYY-MM-DD）。
    優先度: 1) git --diff-filter=A で取得する最初の追加コミット日（バルク編集の影響を受けない）
           2) 通常のgit log
           3) ファイル mtime
    """
    import re
    fpath = os.path.join(REPO_DIR, ticker, fname)
    # 1) 初回追加コミット日（最も堅牢 — バルク編集で書き換えても publish date は保持）
    try:
        result = subprocess.run(
            f'git log --diff-filter=A --format="%ai" --follow -- "{ticker}/{fname}"',
            shell=True, cwd=REPO_DIR, capture_output=True, text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            # 最終行が最古（初回追加）
            lines = [l for l in result.stdout.strip().split("\n") if l.strip()]
            if lines:
                return lines[-1][:10]
    except Exception:
        pass
    # 2) 通常のgit log（最新コミット日）
    try:
        result = subprocess.run(
            f'git log -1 --format="%ai" -- "{ticker}/{fname}"',
            shell=True, cwd=REPO_DIR, capture_output=True, text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()[:10]
    except Exception:
        pass
    # 3) ファイル mtime（フォールバック）
    try:
        mtime = os.path.getmtime(fpath)
        return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
    except Exception:
        return None

def _business_days_ago(days):
    """n営業日前の日付を返す（土日除外、祝日は簡略化のため非考慮）"""
    from datetime import timedelta
    cur = datetime.now()
    remaining = days
    while remaining > 0:
        cur -= timedelta(days=1)
        if cur.weekday() < 5:  # 0=Mon..4=Fri
            remaining -= 1
    return cur.strftime("%Y-%m-%d")

def _collect_recent_reports(ticker_data, limit=7):
    """全ティッカーから直近追加レポート最大N件を日付降順で返す"""
    items = []
    for ticker, reports in ticker_data.items():
        if not reports:
            continue
        latest_q, latest_f = reports[0]
        date_str = _get_report_date(ticker, latest_f)
        if date_str:
            items.append({"ticker": ticker, "quarter": latest_q, "fname": latest_f, "date": date_str})
    items.sort(key=lambda x: x["date"], reverse=True)
    return items[:limit]

def make_root_index(ticker_data):
    from datetime import timedelta
    import re as _re
    # NEW判定: レポート公開から 7営業日 以内
    new_threshold = _business_days_ago(7)
    # タイムライン: 直近追加レポート7件
    recent_items = _collect_recent_reports(ticker_data, limit=7)
    timeline_html = ""
    if recent_items:
        tl_chips = ""
        for item in recent_items:
            is_new_item = item["date"] >= new_threshold
            new_dot = '<span class="tl-new-dot" aria-label="NEW"></span>' if is_new_item else ''
            # MM/DD 表記
            try:
                mmdd = f'{int(item["date"][5:7])}/{int(item["date"][8:10])}'
            except Exception:
                mmdd = item["date"][5:]
            url = f'{PAGES_BASE_URL}/{item["ticker"]}/{item["fname"]}'
            tl_chips += (
                f'<a class="tl-item" href="{url}">'
                f'{new_dot}'
                f'<span class="tl-ticker">{item["ticker"]}</span>'
                f'<span class="tl-quarter">{item["quarter"]}</span>'
                f'<span class="tl-date">{mmdd}</span>'
                f'</a>'
            )
        timeline_html = (
            '<section class="timeline" aria-label="直近追加されたレポート">'
            '<div class="timeline-inner">'
            '<div class="timeline-header"><span class="timeline-label">最新レポート</span><span class="timeline-sub">直近追加 · 最大7件</span></div>'
            f'<div class="timeline-items">{tl_chips}</div>'
            '</div></section>'
        )

    cards = ""
    for ticker in sorted(ticker_data.keys()):
        reports = ticker_data[ticker]
        sector = SECTOR_MAP.get(ticker, "")
        if not sector:
            sector = extract_sector_from_report(ticker) or ""
        if not sector:
            sector = "未分類"
            print(f"  ⚠️  警告: {ticker} のセクターが SECTOR_MAP に未登録です。「未分類」で表示します。SECTOR_MAP に追加してください。")
        latest_q, latest_f = reports[0]

        # 最新レポートの日付を取得してNEW判定（7営業日以内）
        latest_date = _get_report_date(ticker, latest_f)
        is_new = latest_date and latest_date >= new_threshold

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
        if not score:
            print(f"  ⚠️  警告: {ticker} のスコアを自動抽出できませんでした。手動確認が必要です。")
        score_attr = f' data-score="{score}"' if score else ''
        score_html = ''
        if score:
            icon = SCORE_ICONS.get(score, "")
            if score >= 4:
                bg = "rgba(184,145,42,0.15)" if score == 4 else "rgba(184,145,42,0.2)"
                fg = "#B8912A"
                bd = "rgba(184,145,42,0.3)" if score == 4 else "rgba(184,145,42,0.4)"
            elif score == 3:
                bg, fg, bd = "rgba(74,85,104,0.12)", "#4A5568", "rgba(74,85,104,0.25)"
            else:
                bg = "rgba(139,32,32,0.1)" if score == 2 else "rgba(139,32,32,0.12)"
                fg = "#8B2020"
                bd = "rgba(139,32,32,0.2)" if score == 2 else "rgba(139,32,32,0.25)"
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
<title>Atlas Quarterly — 米国決算分析レポート</title>
<meta name="description" content="Atlas Quarterly は米国主要49銘柄の四半期決算をインフォグラフィックで読み解くレポートポータル。セクター別・スコア別に閲覧できます。">
<meta property="og:title" content="Atlas Quarterly — 米国決算分析レポート">
<meta property="og:description" content="米国主要49銘柄の四半期決算を、財務・戦略・バリュエーションの多層視点でインフォグラフィック化。">
<meta property="og:type" content="website">
<meta property="og:url" content="{PAGES_BASE_URL}/">
<meta property="og:image" content="{PAGES_BASE_URL}/apple-touch-icon.png">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary">
<link rel="icon" type="image/png" href="favicon.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho+B1:wght@600;700;800&family=Noto+Sans+JP:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{{--navy:#1A2540;--navy-deep:#0F1829;--gold:#B8912A;--gold-lt:#D4A843;--paper:#F5F2EC;--paper-dk:#E8E3D5;--ink:#0F0E0C;--ink-sub:#4A5568;--ink-mute:#718096;--border:#d4cfc0;--alert:#8B2020}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{font-family:'Noto Sans JP',sans-serif;background:var(--paper);color:var(--ink);line-height:1.75;-webkit-font-smoothing:antialiased}}
.hero{{background:linear-gradient(135deg,var(--navy-deep) 0%,var(--navy) 50%,var(--navy-deep) 100%);color:#fff;padding:72px 32px 60px;text-align:center;position:relative;overflow:hidden;border-bottom:1px solid rgba(184,145,42,0.15)}}
.hero::before{{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 30% 40%,rgba(184,145,42,0.12) 0%,transparent 60%),radial-gradient(ellipse at 70% 60%,rgba(184,145,42,0.08) 0%,transparent 60%)}}
.hero-inner{{position:relative;z-index:1;max-width:960px;margin:0 auto}}
.hero-logo{{height:56px;width:auto;max-width:420px;margin:0 auto 22px;display:block}}
.hero-title{{font-family:'Shippori Mincho B1',serif;font-size:34px;font-weight:800;letter-spacing:2px;color:#fff;margin:0 0 10px;line-height:1.3}}
.hero-sub{{font-size:14px;color:rgba(255,255,255,.7);letter-spacing:.08em;margin:0}}
.hero-meta{{margin-top:22px;font-family:'Inter',sans-serif;font-size:11px;color:rgba(212,168,67,.75);letter-spacing:.2em;text-transform:uppercase}}
.controls{{max-width:1100px;margin:40px auto 0;padding:0 20px}}
.sort-bar{{text-align:center;margin-bottom:20px;display:flex;flex-wrap:wrap;gap:8px;justify-content:center}}
.sort-btn{{font-family:'Noto Sans JP',sans-serif;font-size:13px;font-weight:600;padding:8px 20px;border-radius:8px;border:1px solid var(--border);background:#fff;color:var(--ink-sub);cursor:pointer;transition:all .15s;letter-spacing:.04em}}
.sort-btn.active{{background:var(--navy);color:var(--gold-lt);border-color:var(--navy)}}
.sort-btn:hover:not(.active){{border-color:var(--gold);color:var(--gold)}}
.search-bar{{max-width:440px;margin:0 auto 24px;position:relative}}
.search-bar input{{width:100%;padding:12px 18px 12px 42px;border-radius:10px;border:1px solid var(--border);background:#fff;color:var(--ink);font-family:'Noto Sans JP',sans-serif;font-size:14px;outline:none;transition:border-color .15s,box-shadow .15s}}
.search-bar input:focus{{border-color:var(--gold);box-shadow:0 0 0 3px rgba(184,145,42,.1)}}
.search-bar svg{{position:absolute;left:14px;top:50%;transform:translateY(-50%);color:var(--ink-mute)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:18px;max-width:1100px;margin:0 auto 40px;padding:0 20px}}
.sector-heading{{font-family:'Shippori Mincho B1',serif;color:var(--navy);font-size:18px;font-weight:700;margin:28px 0 8px;padding-bottom:10px;border-bottom:1px solid var(--border);grid-column:1/-1;letter-spacing:.05em}}
.sector-heading::before{{content:'';display:inline-block;width:4px;height:18px;background:var(--gold);margin-right:10px;vertical-align:-3px}}
.card{{background:#fff;border:1px solid var(--border);border-radius:12px;padding:22px;display:flex;flex-direction:column;gap:12px;transition:all .2s;position:relative}}
.card:hover{{border-color:var(--gold);box-shadow:0 4px 18px rgba(26,37,64,.08);transform:translateY(-2px)}}
.card-top{{display:flex;align-items:center;justify-content:space-between;gap:10px}}
.card-id{{display:flex;align-items:center;gap:12px;min-width:0}}
.card-badges{{display:flex;align-items:center;gap:6px;flex-shrink:0}}
.card-logo{{height:30px;width:auto;max-width:44px;object-fit:contain;flex-shrink:0}}
.card-logo[src$=".png"]{{border-radius:4px}}
.ticker{{font-family:'Inter',sans-serif;font-size:22px;font-weight:700;color:var(--navy);white-space:nowrap;letter-spacing:.02em}}
.sector{{font-size:11px;color:var(--ink-sub);background:var(--paper);padding:4px 11px;border-radius:99px;white-space:nowrap;display:inline-block;align-self:flex-start;letter-spacing:.04em;border:1px solid var(--paper-dk)}}
.fy-row{{display:flex;align-items:center;gap:10px;flex-wrap:wrap}}
.fy-label{{font-family:'Inter',sans-serif;font-size:12px;font-weight:700;color:var(--ink-mute);min-width:56px;flex-shrink:0;letter-spacing:.05em}}
.q-pills{{display:flex;gap:6px;flex-wrap:wrap}}
.q-pill{{font-family:'Inter',sans-serif;font-size:12px;font-weight:600;padding:5px 14px;border-radius:6px;background:var(--paper);color:var(--navy);text-decoration:none;border:1px solid var(--paper-dk);transition:all .15s;letter-spacing:.03em}}
.q-pill:hover{{background:var(--navy);color:var(--gold-lt);border-color:var(--navy)}}
.score-badge{{font-family:'Inter',sans-serif;font-size:11px;font-weight:700;padding:3px 9px;border-radius:6px;white-space:nowrap;line-height:1.5;letter-spacing:.03em}}
.new-badge{{font-family:'Inter',sans-serif;font-size:10px;font-weight:700;padding:3px 8px;border-radius:6px;background:#E53935;color:#fff;white-space:nowrap;letter-spacing:.1em;animation:atlas-new-pulse 1.8s ease-in-out infinite;box-shadow:0 0 0 0 rgba(229,57,53,.55)}}
@keyframes atlas-new-pulse{{0%,100%{{opacity:1;box-shadow:0 0 0 0 rgba(229,57,53,.55)}}50%{{opacity:.78;box-shadow:0 0 0 7px rgba(229,57,53,0)}}}}
/* Timeline */
.timeline{{max-width:1100px;margin:28px auto 0;padding:0 20px}}
.timeline-inner{{background:#fff;border:1px solid var(--border);border-radius:12px;padding:18px 20px;box-shadow:0 1px 3px rgba(26,37,64,.04)}}
.timeline-header{{display:flex;align-items:baseline;gap:12px;margin-bottom:12px}}
.timeline-label{{font-family:'Shippori Mincho B1',serif;font-size:14px;font-weight:700;color:var(--navy);letter-spacing:.08em}}
.timeline-label::before{{content:'';display:inline-block;width:4px;height:14px;background:var(--gold);margin-right:8px;vertical-align:-2px}}
.timeline-sub{{font-family:'Inter',sans-serif;font-size:11px;color:var(--ink-mute);letter-spacing:.05em}}
.timeline-items{{display:flex;gap:8px;overflow-x:auto;padding:2px 0 6px;-webkit-overflow-scrolling:touch;scrollbar-width:thin;scrollbar-color:var(--border) transparent}}
.timeline-items::-webkit-scrollbar{{height:4px}}
.timeline-items::-webkit-scrollbar-thumb{{background:var(--border);border-radius:2px}}
.tl-item{{display:inline-flex;align-items:center;gap:8px;padding:8px 14px;border-radius:8px;background:var(--paper);border:1px solid var(--paper-dk);text-decoration:none;flex-shrink:0;transition:all .15s;position:relative}}
.tl-item:hover{{background:var(--navy);border-color:var(--navy);transform:translateY(-1px);box-shadow:0 2px 8px rgba(26,37,64,.12)}}
.tl-item:hover .tl-ticker{{color:var(--gold-lt)}}
.tl-item:hover .tl-quarter,.tl-item:hover .tl-date{{color:rgba(255,255,255,.75)}}
.tl-ticker{{font-family:'Inter',sans-serif;font-size:13px;font-weight:700;color:var(--navy);letter-spacing:.02em;transition:color .15s}}
.tl-quarter{{font-family:'Inter',sans-serif;font-size:11px;font-weight:600;color:var(--ink-sub);letter-spacing:.03em;transition:color .15s}}
.tl-date{{font-family:'Inter',sans-serif;font-size:11px;color:var(--ink-mute);margin-left:2px;transition:color .15s}}
.tl-new-dot{{display:inline-block;width:7px;height:7px;border-radius:50%;background:#E53935;flex-shrink:0;animation:atlas-new-pulse 1.8s ease-in-out infinite;box-shadow:0 0 0 0 rgba(229,57,53,.55)}}
@media(max-width:768px){{
  .timeline{{margin-top:22px;padding:0 14px}}
  .timeline-inner{{padding:14px 16px}}
  .tl-item{{padding:7px 12px;gap:6px}}
  .tl-ticker{{font-size:12px}}
  .tl-quarter,.tl-date{{font-size:10px}}
}}
.card.hidden{{display:none}}
.no-results{{grid-column:1/-1;text-align:center;color:var(--ink-mute);font-size:14px;padding:48px 0}}
.report-footer{{text-align:center;margin-top:50px;padding:36px 20px 30px;border-top:1px solid var(--border);background:#fff;color:var(--ink-mute);font-size:12px;line-height:1.9}}
.report-footer .brand{{font-family:'Shippori Mincho B1',serif;font-weight:800;letter-spacing:.3em;color:var(--gold);font-size:14px;margin-bottom:10px}}
.report-footer .disclaimer{{max-width:720px;margin:8px auto 0;color:var(--ink-mute);font-size:11px;line-height:1.8}}
.scroll-top{{position:fixed;bottom:28px;right:28px;width:44px;height:44px;border-radius:50%;background:var(--navy);border:1px solid rgba(184,145,42,0.3);color:var(--gold-lt);font-size:1.1rem;cursor:pointer;display:flex;align-items:center;justify-content:center;opacity:0;visibility:hidden;transition:all .25s;z-index:100;box-shadow:0 4px 14px rgba(15,24,41,.25)}}
.scroll-top.visible{{opacity:1;visibility:visible}}
.scroll-top:hover{{background:var(--gold);color:var(--navy);border-color:var(--gold)}}
@media(max-width:768px){{
  .hero{{padding:52px 24px 46px}}
  .hero-logo{{height:40px;margin-bottom:16px}}
  .hero-title{{font-size:22px;letter-spacing:1px}}
  .hero-sub{{font-size:12px}}
  .hero-meta{{font-size:10px;margin-top:16px}}
  .controls{{margin-top:28px;padding:0 14px}}
  .grid{{grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px;padding:0 14px}}
  .card{{padding:18px}}
  .ticker{{font-size:18px}}
  .sort-bar{{gap:6px;margin-bottom:16px}}
  .sort-btn{{padding:7px 16px;font-size:12px}}
  .search-bar{{max-width:100%}}
  .report-footer{{margin-top:32px;padding:28px 16px}}
  .scroll-top{{bottom:16px;right:16px;width:40px;height:40px}}
  .sector-heading{{font-size:16px;margin:20px 0 6px}}
}}
@media(max-width:480px){{
  .grid{{grid-template-columns:1fr;gap:12px}}
  .ticker{{font-size:17px}}
  .q-pill{{padding:4px 11px;font-size:11px}}
  .fy-label{{font-size:11px;min-width:48px}}
  .card-top{{flex-wrap:wrap;gap:8px}}
  .hero-title{{font-size:19px}}
}}
</style>
</head><body>
<section class="hero"><div class="hero-inner"><img class="hero-logo" src="logos/atlas-quarterly-type-gold-transparent-1200w.png" alt="Atlas Quarterly"><h1 class="hero-title">米国決算分析レポート</h1><p class="hero-sub">米国主要49銘柄を四半期ごとに定点観測。財務・戦略・バリュエーションを一枚に凝縮。</p><div class="hero-meta">Last Updated — {now}</div></div></section>
{timeline_html}
<div class="controls">
<div class="sort-bar"><button class="sort-btn active" onclick="sortBy('ticker')">ABC順</button><button class="sort-btn" onclick="sortBy('sector')">セクター別</button><button class="sort-btn" onclick="sortBy('score')">スコア順</button></div>
<div class="search-bar"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg><input type="text" id="search" placeholder="ティッカーで検索..." oninput="filterCards()"></div>
</div>
<div class="grid" id="grid">{cards}</div>
<footer class="report-footer">
<div class="brand">ATLAS QUARTERLY</div>
<p class="disclaimer">本レポートは情報提供を目的としたものであり、特定の銘柄の売買を推奨するものではありません。投資判断はご自身の責任でお願いいたします。</p>
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
    # 非ティッカーディレクトリを除外
    NON_TICKER_DIRS = {"legal", "logos", "node_modules"}
    result = {}
    for item in os.listdir(REPO_DIR):
        full = os.path.join(REPO_DIR, item)
        if not os.path.isdir(full) or item.startswith("."):
            continue
        if item in NON_TICKER_DIRS:
            continue
        # ティッカーは大文字A-Zのみ（1〜5文字）
        if not (item.isupper() and item.isalpha() and 1 <= len(item) <= 5):
            continue
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

    # ── 1. HTMLコピー
    os.makedirs(ticker_dir, exist_ok=True)
    if os.path.abspath(html_path) != os.path.abspath(dest_path):
        shutil.copy2(html_path, dest_path)
        print(f"✅ HTMLコピー: {ticker}/{filename}")
    else:
        print(f"✅ HTMLコピー省略（同一ファイル）: {ticker}/{filename}")

    # ── 1b. Atlas nav + Quarterlyバンド注入（新規レポートにも適用）
    inject_script = os.path.expanduser("~/atlas-shared/nav/inject.py")
    if os.path.exists(inject_script):
        try:
            subprocess.run(["python3", inject_script], check=False, capture_output=True)
            print("✅ Atlas nav + Quarterlyバンド注入")
        except Exception as e:
            print(f"⚠️  nav注入失敗: {e}")

    # ── 2. 銘柄index更新
    reports = scan_existing_reports(ticker)
    with open(os.path.join(ticker_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(make_ticker_index(ticker, reports))
    print(f"✅ {ticker}/index.html 更新")

    # ── 3. ルートindex更新
    with open(os.path.join(REPO_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(make_root_index(scan_all_tickers()))
    print("✅ 全銘柄ポータル更新")

    # ── 3b. Atlas共通nav再注入（テーマ切替・ナビリンクを復元）
    inject_script = os.path.expanduser("~/atlas-shared/nav/inject.py")
    if os.path.exists(inject_script):
        try:
            subprocess.run(["python3", inject_script], check=False, capture_output=True)
            print("✅ Atlas共通nav再注入")
        except Exception as e:
            print(f"⚠️  nav注入失敗: {e}")

    # ── 4. Cloudflare Pages にデプロイ
    print("📤 Cloudflare Pages にデプロイ中...")
    run(f"npx wrangler pages deploy {REPO_DIR} --project-name atlas-reports --commit-dirty=true")
    print("✅ デプロイ完了")

    # ── 5. Gitにもコミット（バックアップ・履歴管理用）
    try:
        run("git add -A")
        run(f'git commit -m "Add {ticker} {quarter} report"')
        run("git push origin main")
    except Exception as e:
        print(f"⚠️ Git push スキップ（Cloudflareデプロイは成功済み）: {e}")

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
