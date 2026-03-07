#!/usr/bin/env python3
import sys, os, shutil, subprocess
from datetime import datetime

GITHUB_USERNAME = "yskzz121"
REPO_NAME       = "ui-kabu-reports"
REPO_DIR        = os.path.expanduser(f"~/ui-kabu-reports")
PAGES_BASE_URL  = f"https://{GITHUB_USERNAME}.github.io/{REPO_NAME}"

def run(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, cwd=cwd or REPO_DIR, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"コマンド失敗: {cmd}\n{result.stderr}")
    return result.stdout.strip()

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

def make_root_index(ticker_data):
    cards = ""
    for ticker in sorted(ticker_data.keys()):
        reports = ticker_data[ticker]
        latest_q, latest_f = reports[0]
        url = f"{PAGES_BASE_URL}/{ticker}/{latest_f}"
        ticker_url = f"{PAGES_BASE_URL}/{ticker}/"
        cards += f'<div class="card"><div class="ticker">{ticker}</div><div class="latest">{latest_q}</div><a class="btn" href="{url}">レポートを見る →</a><br><a class="arch" href="{ticker_url}">過去のレポート</a></div>'
    now = datetime.now().strftime("%Y/%m/%d %H:%M")
    return f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>U&I株倶楽部 決算レポート</title>
<style>*{{box-sizing:border-box;margin:0;padding:0}}body{{font-family:sans-serif;background:#0f1117;color:#e0e0e0;padding:40px 20px}}header{{text-align:center;margin-bottom:40px}}header h1{{color:#60a5fa;font-size:1.8rem}}header p{{color:#6b7280;font-size:.9rem;margin-top:8px}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:20px;max-width:960px;margin:0 auto}}.card{{background:#1a1d27;border-radius:12px;padding:24px;display:flex;flex-direction:column;gap:10px}}.ticker{{font-size:1.5rem;font-weight:bold}}.latest{{font-size:.85rem;color:#6b7280}}.btn{{background:#3b82f6;color:white;padding:10px;border-radius:8px;text-decoration:none;font-weight:bold;text-align:center}}.arch{{font-size:.8rem;color:#6b7280;text-align:center}}footer{{text-align:center;margin-top:40px;color:#374151;font-size:.8rem}}</style>
</head><body>
<header><h1>📊 U&I株倶楽部 決算レポート</h1><p>最終更新: {now}</p></header>
<div class="grid">{cards}</div>
<footer>U&I株倶楽部 · Powered by Claude</footer>
</body></html>"""

def scan_existing_reports(ticker):
    ticker_dir = os.path.join(REPO_DIR, ticker)
    if not os.path.exists(ticker_dir):
        return []
    files = sorted([f for f in os.listdir(ticker_dir) if f.endswith(".html") and f != "index.html"], reverse=True)
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

def deploy(html_path, ticker, quarter):
    ticker = ticker.upper()
    html_path = os.path.expanduser(html_path)
    if not os.path.exists(html_path):
        raise FileNotFoundError(f"HTMLファイルが見つかりません: {html_path}")
    filename  = f"{quarter}.html"
    ticker_dir = os.path.join(REPO_DIR, ticker)
    dest_path  = os.path.join(ticker_dir, filename)
    print(f"\n🚀 デプロイ開始: {ticker} {quarter}")
    print("📥 リポジトリを最新化中...")
    run("git pull origin main")
    os.makedirs(ticker_dir, exist_ok=True)
    shutil.copy2(html_path, dest_path)
    print(f"✅ HTMLコピー完了: {ticker}/{filename}")
    reports = scan_existing_reports(ticker)
    with open(os.path.join(ticker_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(make_ticker_index(ticker, reports))
    print(f"✅ {ticker}/index.html 更新")
    with open(os.path.join(REPO_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(make_root_index(scan_all_tickers()))
    print("✅ 全銘柄ポータル更新")
    print("📤 GitHubにプッシュ中...")
    run("git add -A")
    run(f'git commit -m "Add {ticker} {quarter} report"')
    run("git push origin main")
    report_url = f"{PAGES_BASE_URL}/{ticker}/{filename}"
    print(f"""
{'='*55}
🎉 デプロイ完了！

📊 LINEに貼るURL:
   {report_url}

🏠 全銘柄ポータル:
   {PAGES_BASE_URL}/
{'='*55}
""")
    return report_url

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("使い方: python3 deploy_report.py <HTMLパス> <ティッカー> <四半期>")
        print("例    : python3 deploy_report.py ~/Downloads/NVDA.html NVDA FY26Q4")
        sys.exit(1)
    try:
        deploy(sys.argv[1], sys.argv[2], sys.argv[3])
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        sys.exit(1)
