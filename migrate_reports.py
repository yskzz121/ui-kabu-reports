#!/usr/bin/env python3
"""
migrate_reports.py — 旧フォーマット決算レポートHTMLを新3レイヤー構造に一括変換

Usage:
    python3 migrate_reports.py                           # 全ファイル一括変換
    python3 migrate_reports.py GOOGL/FY2025Q4.html       # 特定ファイルのみ
    python3 migrate_reports.py --dry-run GOOGL/FY2025Q4.html  # ドライラン
"""

import sys
import os
import re
import glob
import copy
import traceback
from pathlib import Path

try:
    from bs4 import BeautifulSoup, Comment, NavigableString, Tag
except ImportError:
    print("ERROR: beautifulsoup4 が必要です。pip install beautifulsoup4 を実行してください。")
    sys.exit(1)

BASE_DIR = Path(__file__).resolve().parent

# ── 除外ファイル ──
SKIP_FILES = {
    'TSM/Q1_2026.html',
    'NFLX/Q1_2026.html',
    'GOOGL/FY2025Q4_mobile_test.html',
}

# ── 非レポートファイル（ポータル等）──
NON_REPORT_FILES = {
    'index.html', 'about.html', 'faq.html',
    'index_backup_20260324.html',
    'legal/privacy.html', 'legal/terms.html', 'legal/tokusho.html',
}

# ── 構造が異なるため構造変換スキップするファイル ──
STRUCTURE_SKIP = {
    'RBRK/FY26_通期.html',
}

# ── Layer II セクション ID ──
LAYER2_IDS = {'sec-metrics', 'sec-revenue', 'sec-margin', 'sec-insight', 'sec-guidance'}

# ── Layer III セクション ID → (英語タイトル, 日本語サブタイトル) ──
LAYER3_MAP = {
    'sec-segment':   ('Segments', 'セグメント別売上構成'),
    'sec-geo':       ('Geography', '地域別売上構成'),
    'sec-cashflow':  ('Cash Flow', 'キャッシュフロー'),
    'sec-saas':      ('SaaS KPI', 'SaaS指標'),
    'sec-technical': ('Technical', 'テクニカル分析'),
    'sec-mgmt':      ('Management', '経営陣コメント'),
    'sec-risk':      ('Risk & Catalyst', 'リスク・注目ポイント / カタリスト'),
    'sec-compare':   ('QoQ Compare', '前回決算との比較'),
    'sec-valuation': ('Valuation', '想定株価 3パターン'),
    'sec-ntm-fv':    ('NTM Fair Value', 'NTM想定株価'),
    'sec-ntm':       ('NTM Fair Value', 'NTM想定株価'),
    'sec-analysts':  ('Analysts', 'アナリスト評価'),
    'sec-sentiment': ('Sentiment', 'センチメント分析'),
    # 非標準
    'sec-expense':    ('Expense', '費用分析'),
    'sec-product':    ('Products', 'プロダクト分析'),
    'sec-annual':     ('Annual', '年間業績'),
    'sec-market':     ('Market', '市場分析'),
    'sec-external':   ('External', '外部環境'),
    'sec-highlights': ('Highlights', 'ハイライト'),
    'sec-10k':        ('10-K', '年次報告'),
    'sec-overview':   ('Overview', '企業概要'),
}

# ── スコアラベル ──
SCORE_LABELS = {
    5: '素晴らしい決算',
    4: '良い決算',
    3: '悪くない決算',
    2: '悪い決算',
    1: '壊滅的な決算',
}

# ─────────────────────────────────────────────
# CSS / JS テンプレート (TSM/Q1_2026.html から抽出)
# ─────────────────────────────────────────────

def load_template_css():
    """TSM/Q1_2026.html から行11-567のCSSを読み込む（新構造用CSS）"""
    tsm = BASE_DIR / 'TSM' / 'Q1_2026.html'
    lines = tsm.read_text('utf-8').splitlines()
    css_lines = []
    in_css = False
    for line in lines:
        if '<style>' in line:
            in_css = True
            css_lines.append(line)
            continue
        if '</style>' in line and in_css:
            css_lines.append(line)
            break
        if in_css:
            css_lines.append(line)
    return '\n'.join(css_lines)


def extract_old_content_css(html):
    """旧HTMLのstyleタグからコンテンツ関連CSSを抽出。
    最小限の除外のみ行い、旧コンテンツに必要なCSSを最大限保持する。

    除外するもの:
    - :root { ... } ブロック（新CSSの変数を使用）
    - * { ... }（新CSSのリセットを使用）
    - body { ... }（新CSSのbody定義を使用）
    - html[data-theme] ルール（新CSSのテーマを使用）
    - .header 関連（新 .rh に置き換え済み）
    - .score-* 関連（新 .l1-score に置き換え済み）
    - .overview-dropdown 関連（新 .ov-drop に置き換え済み）
    - .top-panel / .consensus-panel（Layer Iに統合済み）
    - atlas-nav / atlas-floating-tools 関連（保持済み）

    保持するもの:
    - .card, .card-val, .card-label 等のコンテンツカード
    - .grid, .val-cards, .tech-grid 等のレイアウト
    - .quote, .comment-box 等のコメント
    - .data-table, .compare-table 等のテーブル
    - @media クエリ内のコンテンツ関連ルール
    - @keyframes（旧アニメーション）
    - その他全てのコンテンツセクション用CSS
    """
    soup = BeautifulSoup(html, 'html.parser')

    # atlas-nav のstyleは除外（別ブロックとして保持済み）
    old_styles = []
    for style in soup.find_all('style'):
        if style.string:
            # atlas-nav専用CSSはスキップ（.atlas-nav を含むブロック）
            if '.atlas-nav-inner' in (style.string or '') or '.atlas-nav{' in (style.string or '').replace(' ', ''):
                continue
            old_styles.append(style.string)
    if not old_styles:
        return ''

    old_css = '\n'.join(old_styles)

    # 行ベースで除外対象を判定（より堅牢なアプローチ）
    # ブレース深度で管理
    EXCLUDE_SELECTORS = [
        r'^\s*:root\s*\{',
        r'^\s*\*\s*\{',
        r'^\s*body\s*\{',
        r'^\s*body\s*,',
        r'^\s*html\[data-theme',
        r'^\s*h1\s*,\s*h2\s*,\s*h3',
        r'^\s*\.rh\b', r'^\s*\.rh-', r'^\s*\.ov-wrap', r'^\s*\.ov-btn\b', r'^\s*\.ov-drop',
        r'^\s*\.l1\b', r'^\s*\.l1-',
        r'^\s*\.layer-eyebrow', r'^\s*\.boundary',
        r'^\s*\.sec3\b', r'^\s*\.sec3-',
        r'^\s*\.header\b', r'^\s*\.header-content', r'^\s*\.header-logo',
        r'^\s*\.report-header-logo', r'^\s*\.ticker-badge',
        r'^\s*\.score-section', r'^\s*\.score-banner', r'^\s*\.score-big\b',
        r'^\s*\.score-badge', r'^\s*\.score-num\b', r'^\s*\.score-number',
        r'^\s*\.score-label', r'^\s*\.score-dot', r'^\s*\.score-icon', r'^\s*\.score-bar\b',
        r'^\s*\.overview-dropdown', r'^\s*\.overview-toggle',
        r'^\s*\.top-panel', r'^\s*\.consensus-panel',
        r'^\s*\.price-panel\b',
        r'^\s*\.atlas-floating', r'^\s*\.atlas-nav', r'^\s*\.atlas-quarterly',
        r'^\s*\.currency-toggle', r'^\s*\.theme-toggle',
        r'^\s*\.cur-val\b', r'^\s*\.cur-active', r'^\s*\.cur-inactive', r'^\s*\.cur-sep',
        r'^\s*\.portal-link',
        r'^\s*\.toc-nav\b', r'^\s*\.toc-toggle', r'^\s*\.toc-menu', r'^\s*\.toc-list',
        r'^\s*\.toc-expand',
        r'^\s*\.tradingview-widget',
        r'^\s*\.no-currency\b',
    ]

    # CSSルールをブレース深度で分割
    filtered_rules = []
    depth = 0
    current_rule = []
    in_comment = False

    for i in range(len(old_css)):
        ch = old_css[i]
        current_rule.append(ch)

        # コメント検出
        if not in_comment and i + 1 < len(old_css) and old_css[i:i+2] == '/*':
            in_comment = True
        elif in_comment and i >= 1 and old_css[i-1:i+1] == '*/':
            in_comment = False

        if in_comment:
            continue

        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth <= 0:
                depth = 0
                rule_text = ''.join(current_rule).strip()
                current_rule = []

                if not rule_text:
                    continue

                # セレクタ部分を取得
                brace_pos = rule_text.find('{')
                if brace_pos < 0:
                    continue
                selector = rule_text[:brace_pos].strip()

                # @media クエリは特別扱い: 中身を再帰的にフィルタリング
                if selector.startswith('@media'):
                    # @media ブロック内のルールを再帰フィルタ
                    inner_css = rule_text[brace_pos+1:rule_text.rfind('}')].strip()
                    inner_filtered = _filter_css_rules(inner_css, EXCLUDE_SELECTORS)
                    if inner_filtered.strip():
                        filtered_rules.append(f'{selector} {{\n{inner_filtered}\n}}')
                    continue

                # @keyframes は全て保持
                if selector.startswith('@keyframes'):
                    filtered_rules.append(rule_text)
                    continue

                # 除外チェック
                skip = False
                for pattern in EXCLUDE_SELECTORS:
                    if re.search(pattern, selector, re.MULTILINE):
                        skip = True
                        break

                if not skip:
                    filtered_rules.append(rule_text)

    if not filtered_rules:
        return ''

    return '\n/* ── Legacy Content CSS (from original report) ── */\n' + '\n'.join(filtered_rules)


def _filter_css_rules(css_text, exclude_patterns):
    """CSS文字列内の個別ルールをフィルタリング（@media内用）"""
    filtered = []
    depth = 0
    current = []
    in_comment = False

    for i in range(len(css_text)):
        ch = css_text[i]
        current.append(ch)

        if not in_comment and i + 1 < len(css_text) and css_text[i:i+2] == '/*':
            in_comment = True
        elif in_comment and i >= 1 and css_text[i-1:i+1] == '*/':
            in_comment = False

        if in_comment:
            continue

        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth <= 0:
                depth = 0
                rule = ''.join(current).strip()
                current = []
                if not rule:
                    continue

                brace = rule.find('{')
                if brace < 0:
                    continue
                sel = rule[:brace].strip()

                skip = False
                for pat in exclude_patterns:
                    if re.search(pat, sel, re.MULTILINE):
                        skip = True
                        break

                if not skip:
                    filtered.append(rule)

    return '\n'.join(filtered)


def load_template_js():
    """TSM/Q1_2026.html から Accordion/TOC/Overview/Insight/Risk/Tooltip JS を読み込む"""
    tsm = BASE_DIR / 'TSM' / 'Q1_2026.html'
    content = tsm.read_text('utf-8')

    # Script block 1: Accordion/TOC/Overview/Insight/Risk/Tooltip (行1686-1783)
    m1 = re.search(r'<script>\s*\n// ── Accordion ──.*?</script>', content, re.DOTALL)
    js1 = m1.group(0) if m1 else ''

    # Script block 2: Currency Toggle (行1786-1926)
    m2 = re.search(r'<!-- Currency Toggle.*?</script>', content, re.DOTALL)
    js2 = m2.group(0) if m2 else ''

    # Script block 3: Theme Toggle (行1929-1950)
    m3 = re.search(r'<!-- Theme Toggle.*?</script>', content, re.DOTALL)
    js3 = m3.group(0) if m3 else ''

    return js1, js2, js3


# ─────────────────────────────────────────────
# ユーティリティ関数
# ─────────────────────────────────────────────

def extract_text(el):
    """要素からテキストを抽出（Noneセーフ）"""
    if el is None:
        return ''
    return el.get_text(strip=True)


def extract_score(soup):
    """旧HTMLからスコア数値とラベルを抽出"""
    score = None
    label = ''
    comment = ''

    # Pattern 1: score-num or score-number (GEN3: JPM style — direct number)
    el = soup.find(class_='score-num') or soup.find(class_='score-number')
    if el:
        txt = extract_text(el)
        m = re.search(r'(\d)', txt)
        if m:
            score = int(m.group(1))

    # Pattern 2: score-banner → score-label text (GEN1: NVDA style — "スコア 5／5")
    if score is None and soup.find(class_='score-banner'):
        banner = soup.find(class_='score-banner')
        lbl = banner.find(class_='score-label')
        if lbl:
            txt = extract_text(lbl)
            m = re.search(r'(\d)', txt)
            if m:
                score = int(m.group(1))

    # Pattern 3: score-dot active count (reliable — takes priority over ambiguous label text)
    if score is None:
        dots = soup.find_all(class_='score-dot')
        if dots:
            active_count = sum(1 for d in dots if 'active' in d.get('class', []))
            if active_count > 0:
                score = active_count

    # Pattern 4: score-label text (GEN2: "4 / 5 — 良い決算")
    if score is None:
        lbl_el = soup.find(class_='score-label')
        if lbl_el:
            txt = extract_text(lbl_el)
            m = re.search(r'(\d)\s*[/／]\s*5', txt)
            if m:
                score = int(m.group(1))
            else:
                # Only extract leading digit if it looks like a score (1-5 at start)
                m2 = re.match(r'^[^\d]*(\d)\b', txt)
                if m2 and int(m2.group(1)) <= 5:
                    score = int(m2.group(1))

    # Pattern 5: score-big text with digit (rare)
    if score is None and soup.find(class_='score-big'):
        el = soup.find(class_='score-big')
        txt = extract_text(el)
        m = re.search(r'(\d)', txt)
        if m:
            score = int(m.group(1))

    # Default
    if score is None:
        score = 3

    score = max(1, min(5, score))

    # Extract label
    lbl_el = soup.find(class_='score-label')
    if lbl_el:
        raw_label = extract_text(lbl_el)
        # Clean: remove "スコア X／5" prefix and "X / 5 —" prefix
        cleaned = re.sub(r'^スコア\s*\d+\s*[／/]\s*\d+\s*[—–\-]?\s*', '', raw_label)
        cleaned = re.sub(r'^\d+\s*[／/]\s*\d+\s*[—–\-]?\s*', '', cleaned)
        cleaned = re.sub(r'^スコア\s*', '', cleaned)
        # Strip leading emojis
        cleaned = re.sub(r'^[\U0001F300-\U0001FAFF\U00002702-\U000027B0\u2600-\u26FF\u2700-\u27BF\U0001F900-\U0001F9FF\u200d\ufe0f⏸️]+\s*', '', cleaned)
        cleaned = cleaned.strip()
        # Only use if it looks like a known label (not a full sentence description)
        if cleaned and len(cleaned) < 20:
            label = cleaned

    if not label:
        label = SCORE_LABELS.get(score, '悪くない決算')

    # Extract description/comment
    desc_el = soup.find(class_='score-desc')
    if desc_el:
        comment = extract_text(desc_el)
    comment_el = soup.find(class_='score-comment')
    if comment_el:
        c = extract_text(comment_el)
        if c:
            comment = c

    return score, label, comment


def extract_header_info(soup):
    """旧ヘッダーからロゴ、ティッカー、h1、subtitle、date を抽出"""
    header = soup.find(class_='header')
    if not header:
        return {}

    info = {}

    # Logo
    logo = header.find('img', class_='report-header-logo')
    if not logo:
        logo = header.find('img')
    if logo:
        info['logo_src'] = logo.get('src', '')
        info['logo_alt'] = logo.get('alt', '')
        info['logo_style'] = logo.get('style', '')

    # Ticker badge
    badge = header.find(class_='ticker-badge')
    if badge:
        info['ticker_text'] = extract_text(badge)
    else:
        info['ticker_text'] = ''

    # h1
    h1 = header.find('h1')
    if h1:
        info['h1'] = ''.join(str(c) for c in h1.children)
    else:
        info['h1'] = ''

    # subtitle
    sub = header.find(class_='subtitle')
    if sub:
        info['subtitle'] = ''.join(str(c) for c in sub.children)
    else:
        info['subtitle'] = ''

    # date
    date = header.find(class_='date')
    if date:
        info['date'] = ''.join(str(c) for c in date.children)
    else:
        info['date'] = ''

    return info


def extract_overview_content(soup):
    """企業概要のHTMLコンテンツを抽出"""
    # GEN3: overview-dropdown
    ov = soup.find(class_='overview-dropdown')
    if ov:
        return ov.decode_contents()

    # GEN3 alt: #ovDrop
    ov = soup.find(id='ovDrop')
    if ov:
        return ov.decode_contents()

    # GEN2: #sec-overview section
    ov = soup.find(id='sec-overview')
    if ov:
        body = ov.find(class_='section-body')
        if body:
            return body.decode_contents()
        # section-title を除いた中身
        title = ov.find(class_='section-title')
        content_parts = []
        for child in ov.children:
            if child == title:
                continue
            content_parts.append(str(child))
        return ''.join(content_parts)

    # overview class
    ov = soup.find(class_='overview')
    if ov:
        return ov.decode_contents()

    return ''


def extract_consensus_table(soup):
    """コンセンサステーブルのHTMLを抽出"""
    # GEN3: top-panel → consensus-panel/table
    tp = soup.find(class_='top-panel')
    if tp:
        cp = tp.find(class_='consensus-panel')
        if cp:
            tbl = cp.find('table')
            if tbl:
                return str(tbl)

    # GEN3 alt: consensus-table class
    tbl = soup.find('table', class_='consensus-table')
    if tbl:
        return str(tbl)

    # GEN2/GEN3: #sec-consensus section の中のテーブル
    sec = soup.find(id='sec-consensus')
    if sec:
        tbl = sec.find('table')
        if tbl:
            return str(tbl)

    return ''


def extract_price_panel(soup):
    """株価パネルのHTMLコンテンツを抽出"""
    # GEN3: top-panel → price-panel
    tp = soup.find(class_='top-panel')
    if tp:
        pp = tp.find(class_='price-panel')
        if pp:
            return pp.decode_contents()

    # price-card class
    pp = soup.find(class_='price-panel')
    if pp:
        return pp.decode_contents()

    pp = soup.find(class_='price-card')
    if pp:
        return pp.decode_contents()

    return ''


def extract_chartjs_scripts(soup):
    """Chart.jsのデータスクリプトを全て抽出"""
    scripts = []
    for script in soup.find_all('script'):
        text = script.string or ''
        # Chart.js データスクリプトを識別
        if 'new Chart' in text or 'Chart(' in text:
            scripts.append(str(script))
    return scripts


def extract_atlas_nav(soup):
    """ATLAS-NAV セクション全体（HTML + style + script）を抽出"""
    # コメントで囲まれた ATLAS-NAV 部分を文字列ベースで取得
    return None  # 元HTMLから保持するためNone（後で文字列操作で処理）


def find_atlas_fx(html):
    """window.ATLAS_FX の行を見つけて返す"""
    m = re.search(r'<script>window\.ATLAS_FX\s*=\s*\{[^}]+\};\s*</script>', html)
    if m:
        return m.group(0)
    return ''


def find_atlas_access_meta(html):
    """atlas-access meta タグを見つけて返す"""
    m = re.search(r'<meta\s+name="atlas-access"[^>]*>', html)
    if m:
        return m.group(0)
    return ''


def find_atlas_nav_block(html):
    """ATLAS-NAV-START から ATLAS-NAV-END までのブロック（style/script含む）を抽出"""
    m = re.search(r'<!-- ATLAS-NAV-START -->.*?<!-- ATLAS-NAV-END -->', html, re.DOTALL)
    if m:
        return m.group(0)
    return ''


def find_atlas_nav_script(html):
    """ATLAS-NAV-END 直後の <script>...</script> を抽出（navロジック）"""
    m = re.search(r'<!-- ATLAS-NAV-END -->\s*\n(<!-- ATLAS-QUARTERLY-BAND.*?)\n<!--', html, re.DOTALL)
    # Atlas nav script is after the nav style block
    # Look for the script that follows the nav style
    nav_end_pos = html.find('<!-- ATLAS-NAV-END -->')
    if nav_end_pos < 0:
        return ''
    # Find the associated style block (atlas-nav CSS)
    after_nav = html[nav_end_pos:]
    # The nav style block starts right before ATLAS-NAV-END and ends after it
    # Actually, looking at structure: after ATLAS-NAV-END there's a <style> for atlas-nav, then <script> for nav logic
    style_m = re.search(r'(<style>\s*\.atlas-nav\{.*?</style>)', after_nav, re.DOTALL)
    script_m = re.search(r'(<script>\s*\(function\(\)\{\s*var nav = document\.querySelector.*?</script>)', after_nav, re.DOTALL)
    result = ''
    if style_m:
        result += style_m.group(1) + '\n'
    if script_m:
        result += script_m.group(1)
    return result


def find_quarterly_band(html):
    """ATLAS-QUARTERLY-BAND を抽出"""
    m = re.search(r'<!-- ATLAS-QUARTERLY-BAND-START -->.*?<!-- ATLAS-QUARTERLY-BAND-END -->', html, re.DOTALL)
    if m:
        return m.group(0)
    return ''


def find_floating_tools(html):
    """atlas-floating-tools ブロックを抽出"""
    m = re.search(r'<div class="atlas-floating-tools">.*?</div>\s*\n', html, re.DOTALL)
    if m:
        return m.group(0)
    # 旧形式: atlas-floating-currency
    m = re.search(r'<div class="atlas-floating-currency">.*?</div>\s*\n', html, re.DOTALL)
    if m:
        return m.group(0)
    return ''


def extract_sections_by_id(soup):
    """id="sec-*" を持つ全セクションを抽出し、辞書で返す"""
    sections = {}
    for el in soup.find_all(True, id=re.compile(r'^sec-')):
        sec_id = el.get('id')
        sections[sec_id] = el
    return sections


def get_section_title_text(section):
    """セクションのタイトルテキストを抽出（アイコン絵文字を除去）"""
    title = section.find(class_='section-title')
    if not title:
        title = section.find(class_='section-header')
    if title:
        txt = extract_text(title)
        # 絵文字アイコンを除去
        txt = re.sub(r'^[\U0001F300-\U0001FAFF\U00002702-\U000027B0\u2600-\u26FF\u2700-\u27BF\U0001F900-\U0001F9FF\u200d\ufe0f]+\s*', '', txt)
        return txt.strip()
    return ''


def section_inner_html(section):
    """セクションの中身HTMLを取得（section-title/section-bodyの構造を保持）"""
    return section.decode_contents()


def build_l1_consensus(table_html):
    """旧コンセンサステーブルをL1コンセンサス形式に変換"""
    if not table_html:
        return ''

    # Parse the table
    tbl_soup = BeautifulSoup(table_html, 'html.parser')
    table = tbl_soup.find('table')
    if not table:
        return ''

    # Replace class to l1-consensus-tbl
    table['class'] = ['l1-consensus-tbl']

    # Update cell classes
    for td in table.find_all('td'):
        classes = td.get('class', [])
        # Keep existing lbl/cn/val/beat/neu classes if they exist
        # Add them if not present based on position
        pass  # Table structure varies, keep as-is with new wrapper class

    return f'''<div class="l1-consensus">
    <div class="l1-consensus-head">Consensus vs 実績</div>
    {str(table)}
  </div>'''


def build_l1_price(price_html):
    """旧株価パネルをL1株価行に変換"""
    if not price_html:
        return ''

    psoup = BeautifulSoup(price_html, 'html.parser')

    # Try to extract price values
    cells = []

    # Look for specific patterns
    # Pattern: price-row with labeled items
    price_items = psoup.find_all(class_='price-item')
    if price_items:
        for item in price_items:
            lbl_el = item.find(class_='price-label')
            val_el = item.find(class_='price-value') or item.find(class_='price')
            lbl = extract_text(lbl_el) if lbl_el else ''
            val = extract_text(val_el) if val_el else ''
            if lbl and val:
                classes = 'val'
                if '反応' in lbl or 'reaction' in lbl.lower():
                    classes = 'val react'
                cells.append(f'<div class="l1-price-cell"><div class="lbl">{lbl}</div><div class="{classes}">{val}</div></div>')
    else:
        # Just wrap the raw content
        cells.append(f'<div class="l1-price-cell">{price_html}</div>')

    if not cells:
        return ''

    return f'''<div class="l1-price no-currency">
    {"".join(cells)}
  </div>'''


def build_new_header(info, overview_html):
    """新フォーマットのヘッダーHTMLを生成"""
    logo_html = ''
    if info.get('logo_src'):
        style = ''
        if info.get('logo_style'):
            style = f' style="{info["logo_style"]}"'
        elif info.get('logo_src', '').endswith('.png'):
            style = ' style="border-radius:8px"'
        logo_html = f'<img class="rh-logo" src="{info["logo_src"]}" alt="{info.get("logo_alt", "")}"{ style}>'

    ticker_html = ''
    if info.get('ticker_text'):
        ticker_html = f'<div class="rh-ticker">{info["ticker_text"]}</div>'

    h1_html = info.get('h1', '')
    sub_html = info.get('subtitle', '')
    date_html = info.get('date', '')

    # Replace "Atlas Quarterly" if missing in date
    if date_html and 'Atlas' not in date_html:
        date_html += ' ｜ Atlas Quarterly'

    return f'''<header class="rh">
  <div class="ov-wrap">
    <button class="ov-btn" id="ovBtn" onclick="toggleOverview()">企業概要 <span class="chev">▼</span></button>
  </div>
  <div class="rh-inner">
    <div class="rh-logo-row">
      {logo_html}
      {ticker_html}
    </div>
    <h1>{h1_html}</h1>
    <div class="rh-sub">{sub_html}</div>
    <div class="rh-date">{date_html}</div>
  </div>
</header>

<!-- 企業概要（折りたたみ） -->
<div class="ov-drop" id="ovDrop">
{overview_html}
</div>'''


def build_layer1(score, label, comment, consensus_html, price_html):
    """Layer I セクションを生成"""
    # Notes: use comment as note, or label if no comment
    notes_html = ''
    if comment:
        # Split comment into up to 3 lines on sentence boundaries
        parts = re.split(r'[。．]', comment)
        parts = [p.strip() for p in parts if p.strip()]
        notes = parts[:3]
        if notes:
            notes_lines = '\n'.join(f'    <div class="l1-note">{n}。</div>' if not n.endswith('。') else f'    <div class="l1-note">{n}</div>' for n in notes)
            notes_html = f'''<div class="l1-notes">
    <div class="l1-notes-head">Today's Points</div>
{notes_lines}
  </div>'''
    elif label:
        notes_html = f'''<div class="l1-notes">
    <div class="l1-notes-head">Today's Points</div>
    <div class="l1-note">{label}</div>
  </div>'''

    consensus_block = consensus_html if consensus_html else ''
    price_block = price_html if price_html else ''

    return f'''<div class="layer-eyebrow">Layer I — Executive Summary</div>
<section class="l1">
  <div class="l1-score">
    <div class="l1-score-badge">
      <span class="l1-score-num">{score}</span>
      <span class="l1-score-label">{label}</span>
    </div>
  </div>

  {consensus_block}

  {notes_html}

  {price_block}
</section>'''


def build_boundary():
    """境界マークHTML"""
    return '''<!-- ══ BOUNDARY — Roman Numeral II ══ -->
<div class="boundary">
  <div class="boundary-line"></div>
  <div class="boundary-mark">II</div>
  <div class="boundary-line"></div>
</div>'''


def convert_section_to_sec3(section_el, sec_id):
    """旧 .section を .sec3 に変換"""
    # Get title and body
    title_el = section_el.find(class_='section-title')
    if not title_el:
        title_el = section_el.find(class_='section-header')
    body_el = section_el.find(class_='section-body')

    # Get English/Japanese title
    if sec_id in LAYER3_MAP:
        en_title, jp_title = LAYER3_MAP[sec_id]
    else:
        # Non-standard: use original title
        orig_title = extract_text(title_el) if title_el else sec_id
        # Clean emoji
        orig_title = re.sub(r'^[\U0001F300-\U0001FAFF\U00002702-\U000027B0\u2600-\u26FF\u2700-\u27BF\U0001F900-\U0001F9FF\u200d\ufe0f]+\s*', '', orig_title)
        en_title = sec_id.replace('sec-', '').replace('-', ' ').title()
        jp_title = orig_title

    # Build new sec3 HTML
    has_accordion = 'data-accordion' in str(section_el) if section_el else False
    accordion_attr = ' data-accordion' if has_accordion else ''

    # Get body content
    if body_el:
        body_content = body_el.decode_contents()
    elif title_el:
        # Everything after the title
        parts = []
        found_title = False
        for child in section_el.children:
            if child == title_el:
                found_title = True
                continue
            if found_title:
                parts.append(str(child))
        body_content = ''.join(parts)
    else:
        body_content = section_el.decode_contents()

    return f'''<section class="sec3"{accordion_attr} id="{sec_id}">
  <div class="sec3-title">{en_title} <span class="jp">· {jp_title}</span></div>
  <div class="sec3-body">
{body_content}
  </div>
</section>'''


def build_toc(layer2_ids, layer3_ids):
    """TOCナビゲーションを生成"""
    items = []
    label_map = {
        'sec-metrics': 'Key Metrics',
        'sec-revenue': '売上高 / EPS 7Q推移',
        'sec-margin': '利益率トレンド',
        'sec-insight': '今回のポイント',
        'sec-guidance': 'ガイダンス・見通し',
        'sec-segment': 'セグメント別売上',
        'sec-geo': '地域別売上構成',
        'sec-cashflow': 'キャッシュフロー',
        'sec-saas': 'SaaS KPI',
        'sec-technical': 'テクニカル分析',
        'sec-mgmt': '経営陣コメント',
        'sec-risk': 'リスク・カタリスト',
        'sec-compare': '前回決算比較',
        'sec-valuation': 'バリュエーション',
        'sec-ntm-fv': 'NTM想定株価',
        'sec-ntm': 'NTM想定株価',
        'sec-analysts': 'アナリスト評価',
        'sec-sentiment': 'センチメント分析',
    }

    for sid in layer2_ids + layer3_ids:
        label = label_map.get(sid, sid.replace('sec-', '').replace('-', ' ').title())
        items.append(f'      <li><a href="#{sid}" onclick="tocJump(\'{sid}\')"><span>{label}</span></a></li>')

    items_html = '\n'.join(items)
    return f'''<nav class="toc-nav" id="tocNav">
  <div class="toc-menu" id="tocMenu">
    <div class="toc-expand-all">
      <button onclick="toggleAllSections(true)">すべて展開</button>
      <button onclick="toggleAllSections(false)">すべて折りたたむ</button>
    </div>
    <ul class="toc-list">
{items_html}
    </ul>
  </div>
</nav>
<button class="toc-toggle" id="tocToggle" onclick="toggleToc()">☰</button>'''


def build_footer(footer_text, ticker='', quarter=''):
    """新フォーマットのフッターを生成"""
    if not footer_text:
        footer_text = '''<p>
    本レポートは公開情報に基づく分析であり、<strong>投資助言を目的としたものではありません</strong>。<br>
    投資判断はご自身の責任で行ってください。
  </p>'''

    footer_id = ''
    if ticker and quarter:
        footer_id = f'{ticker} ｜ {quarter} ｜ Atlas Quarterly'
    else:
        footer_id = 'Atlas Quarterly'

    return f'''<div class="footer">
  {footer_text}
  <div class="footer-id">
    {footer_id}
  </div>
</div>'''


def extract_footer_content(soup):
    """旧フッターの中身を抽出"""
    footer = soup.find(class_='footer')
    if footer:
        # footer-id を除く
        fid = footer.find(class_='footer-id')
        content = ''
        for child in footer.children:
            if child == fid:
                continue
            s = str(child).strip()
            if s:
                content += s + '\n'
        return content.strip()
    return ''


def infer_ticker_quarter(filepath):
    """ファイルパスからティッカーと四半期を推定"""
    parts = Path(filepath).parts
    ticker = parts[-2] if len(parts) >= 2 else ''
    quarter = Path(filepath).stem
    return ticker, quarter


# ─────────────────────────────────────────────
# メイン変換関数
# ─────────────────────────────────────────────

def migrate_html(filepath, dry_run=False):
    """1ファイルの変換を実行"""
    rel = str(Path(filepath).relative_to(BASE_DIR))
    ticker, quarter = infer_ticker_quarter(filepath)

    print(f"\n{'='*60}")
    print(f"処理中: {rel}")
    print(f"{'='*60}")

    # 既に新フォーマットかチェック
    html = Path(filepath).read_text('utf-8')
    if 'class="rh"' in html and 'class="l1"' in html and 'class="sec3"' in html:
        print(f"  SKIP: 既に新フォーマット")
        return True

    # STRUCTURE_SKIP チェック
    if rel in STRUCTURE_SKIP:
        print(f"  WARNING: 構造が完全に異なるため、CSS/JS置換のみ実行")
        return migrate_css_js_only(filepath, html, dry_run)

    # Parse
    soup = BeautifulSoup(html, 'html.parser')

    # ── 1. ヘッド部分を構築 ──
    head = soup.find('head')
    title_el = head.find('title') if head else None
    title_text = str(title_el) if title_el else '<title>決算分析 — Atlas Quarterly</title>'

    # ATLAS_FX
    atlas_fx = find_atlas_fx(html)

    # atlas-access meta
    atlas_access = find_atlas_access_meta(html)

    # ── 2. テンプレートCSS読み込み + 旧コンテンツCSS統合 ──
    # 順序: 旧コンテンツCSS → 新構造CSS（新が後で上書き＝新構造が優先）
    template_css = load_template_css()
    legacy_css = extract_old_content_css(html)
    if legacy_css:
        # 旧CSSを <style> 直後に挿入（新CSSが後に来て上書き）
        template_css = template_css.replace('<style>', '<style>\n' + legacy_css + '\n')

    # ── 3. Atlas Nav ブロック保持 ──
    atlas_nav_block = find_atlas_nav_block(html)
    atlas_nav_extra = find_atlas_nav_script(html)
    quarterly_band = find_quarterly_band(html)

    # ── 4. ヘッダー情報抽出 ──
    header_info = extract_header_info(soup)
    if not header_info:
        print(f"  WARNING: ヘッダーが見つかりません")
        header_info = {'h1': ticker, 'subtitle': quarter, 'date': '', 'ticker_text': f'{ticker}', 'logo_src': f'../logos/{ticker}.svg', 'logo_alt': ticker}

    # ── 5. 企業概要抽出 ──
    overview_html = extract_overview_content(soup)

    # ── 6. スコア抽出 ──
    score, label, comment = extract_score(soup)
    print(f"  スコア: {score} ({label})")

    # ── 7. コンセンサステーブル抽出 ──
    consensus_table = extract_consensus_table(soup)
    l1_consensus = build_l1_consensus(consensus_table)

    # ── 8. 株価パネル抽出 ──
    price_html = extract_price_panel(soup)
    l1_price = build_l1_price(price_html)

    # ── 9. セクション分類 ──
    all_sections = extract_sections_by_id(soup)
    print(f"  セクション数: {len(all_sections)}")
    for sid in all_sections:
        print(f"    - {sid}")

    # Layer II セクション
    layer2_sections = []
    layer2_ids_found = []
    for sid in ['sec-metrics', 'sec-revenue', 'sec-margin', 'sec-insight', 'sec-guidance']:
        if sid in all_sections:
            layer2_sections.append((sid, all_sections[sid]))
            layer2_ids_found.append(sid)

    # Layer III セクション（残り全て）
    layer3_sections = []
    layer3_ids_found = []

    # 定義順にまず配置
    ordered_l3 = ['sec-segment', 'sec-geo', 'sec-cashflow', 'sec-saas', 'sec-technical',
                   'sec-mgmt', 'sec-risk', 'sec-compare', 'sec-valuation', 'sec-ntm-fv',
                   'sec-ntm', 'sec-analysts', 'sec-sentiment']
    for sid in ordered_l3:
        if sid in all_sections and sid not in LAYER2_IDS:
            # sec-overview は overview-dropdown に移動したのでスキップ（既にL3マップにはあるが特別扱い）
            if sid == 'sec-overview' and overview_html:
                continue
            layer3_sections.append((sid, all_sections[sid]))
            layer3_ids_found.append(sid)

    # 残りの非標準セクション
    for sid, sec_el in all_sections.items():
        if sid not in LAYER2_IDS and sid not in [s[0] for s in layer3_sections]:
            # sec-consensus は L1 に統合済み→スキップ (ただしL1に入らなかった場合は残す)
            if sid == 'sec-consensus' and l1_consensus:
                continue
            # sec-overview は ov-drop に移動済み→スキップ
            if sid == 'sec-overview' and overview_html:
                continue
            layer3_sections.append((sid, sec_el))
            layer3_ids_found.append(sid)

    # ── 10. Chart.js スクリプト抽出 ──
    chart_scripts = extract_chartjs_scripts(soup)
    print(f"  Chart.jsスクリプト数: {len(chart_scripts)}")

    # ── 11. TradingView ウィジェット抽出 ──
    tradingview_html = ''
    tv_containers = soup.find_all(class_='tradingview-widget-container')
    tv_strings = [str(c) for c in tv_containers]

    # ── 12. Floating tools 抽出 ──
    floating_tools = find_floating_tools(html)
    if not floating_tools:
        floating_tools = '''<div class="atlas-floating-tools">
  <button class="currency-toggle" aria-label="通貨切替 USD/JPY" onclick="toggleCurrency()" title="通貨切替 USD⇄JPY"><span class="cur-active">$</span><span class="cur-sep">/</span><span class="cur-inactive">¥</span></button>
  <button class="theme-toggle-btn" aria-label="テーマ切替" onclick="toggleAtlasTheme()" title="テーマ切替">🌙</button>
</div>'''

    # ── 13. フッター抽出 ──
    footer_content = extract_footer_content(soup)

    # ── 14. JS テンプレート読み込み ──
    js_accordion, js_currency, js_theme = load_template_js()

    # ─────────────────────────────────────────────
    # 新HTML組み立て
    # ─────────────────────────────────────────────

    # Google Fonts
    fonts_link = '<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho+B1:wght@500;700;800&family=Noto+Serif+JP:wght@300;400;600&family=Noto+Sans+JP:wght@300;400;500;700;900&family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet"/>'

    # Chart.js CDN
    chartjs_cdn = '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>'

    new_html_parts = []

    # DOCTYPE + head
    new_html_parts.append(f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
{title_text}
<link rel="icon" type="image/png" href="../favicon.png">
{fonts_link}
{chartjs_cdn}
{atlas_fx}
{template_css}
{atlas_access}
</head>
<body>
''')

    # Atlas Nav
    if atlas_nav_block:
        new_html_parts.append(atlas_nav_block + '\n')
        if atlas_nav_extra:
            new_html_parts.append(atlas_nav_extra + '\n')

    # Quarterly Band
    if quarterly_band:
        new_html_parts.append(quarterly_band + '\n\n')

    # Header
    new_header = build_new_header(header_info, overview_html)
    new_html_parts.append(new_header + '\n\n')

    # Layer I
    l1_html = build_layer1(score, label, comment, l1_consensus, l1_price)
    new_html_parts.append(l1_html + '\n\n')

    # Layer II eyebrow
    new_html_parts.append('<div class="layer-eyebrow">Layer II — 決算の全体像</div>\n\n')

    # Layer II sections (convert div→section, keep .section class)
    for sid, sec_el in layer2_sections:
        sec_html = str(sec_el)
        # Convert <div class="section" ...> to <section class="section" ...>
        sec_html = re.sub(r'^<div(\s+class="section")', r'<section\1', sec_html)
        sec_html = re.sub(r'</div>\s*$', '</section>', sec_html)
        # Remove section-icon emoji spans
        sec_html = re.sub(r'<span class="section-icon">[\s\S]*?</span>\s*', '', sec_html)
        new_html_parts.append(sec_html + '\n\n')

    # Boundary
    new_html_parts.append(build_boundary() + '\n\n')

    # Layer III eyebrow
    new_html_parts.append('<div class="layer-eyebrow">Layer III — Granular Analysis</div>\n\n')

    # Layer III sections (convert to .sec3)
    for sid, sec_el in layer3_sections:
        sec3_html = convert_section_to_sec3(sec_el, sid)
        new_html_parts.append(sec3_html + '\n\n')

    # Footer
    footer_html = build_footer(footer_content, ticker, quarter)
    new_html_parts.append(footer_html + '\n\n')

    # Floating tools
    new_html_parts.append(floating_tools + '\n\n')

    # TOC
    toc_html = build_toc(layer2_ids_found, layer3_ids_found)
    new_html_parts.append(toc_html + '\n\n')

    # JS: Accordion/TOC/Overview/Insight/Risk/Tooltip
    new_html_parts.append(js_accordion + '\n\n')

    # JS: Currency Toggle
    new_html_parts.append(js_currency + '\n\n')

    # JS: Theme Toggle
    new_html_parts.append(js_theme + '\n\n')

    # Chart.js scripts
    for cs in chart_scripts:
        new_html_parts.append(cs + '\n\n')

    # Close
    new_html_parts.append('</body>\n</html>')

    result = ''.join(new_html_parts)

    # ── 15. 検証 ──
    warnings = validate(result, rel)
    for w in warnings:
        print(f"  {w}")

    # ── 16. 出力 ──
    if dry_run:
        print(f"\n  [DRY RUN] 変換結果は{len(result)}文字（上書きなし）")
        return len(warnings) == 0 or all('WARNING' in w for w in warnings)
    else:
        # バックアップ
        backup_path = Path(filepath).with_name(f"{quarter}_old.html")
        if not backup_path.exists():
            Path(filepath).rename(backup_path)
            print(f"  バックアップ: {backup_path.name}")
        else:
            print(f"  バックアップ: {backup_path.name} (既存、スキップ)")

        # 書き込み
        Path(filepath).write_text(result, 'utf-8')
        print(f"  変換完了: {rel} ({len(result):,} bytes)")
        return True


def migrate_css_js_only(filepath, html, dry_run=False):
    """CSS/JSのみ置換（構造変換はスキップ）"""
    rel = str(Path(filepath).relative_to(BASE_DIR))
    ticker, quarter = infer_ticker_quarter(filepath)

    template_css = load_template_css()
    js_accordion, js_currency, js_theme = load_template_js()

    # Replace first <style>...</style> block with template CSS
    result = re.sub(r'<style>.*?</style>', template_css, html, count=1, flags=re.DOTALL)

    # Replace accordion/TOC/overview JS blocks
    # Remove old accordion JS
    result = re.sub(r'<script>\s*//\s*Accordion.*?</script>', '', result, flags=re.DOTALL)
    result = re.sub(r'<script>\s*var touchStartY.*?</script>', '', result, flags=re.DOTALL)
    # Remove old TOC JS
    result = re.sub(r'<script>\s*function toggleToc\(\).*?</script>', '', result, flags=re.DOTALL)
    # Remove old currency/theme JS (be careful not to remove Chart.js)
    result = re.sub(r'<!-- Currency Toggle.*?</script>', '', result, flags=re.DOTALL)
    result = re.sub(r'<!-- Theme Toggle.*?</script>', '', result, flags=re.DOTALL)

    # Add new JS before </body>
    new_js = f'\n{js_accordion}\n\n{js_currency}\n\n{js_theme}\n'
    result = result.replace('</body>', f'{new_js}\n</body>')

    if dry_run:
        print(f"  [DRY RUN] CSS/JS置換のみ: {len(result)}文字")
        return True

    # Backup
    backup_path = Path(filepath).with_name(f"{quarter}_old.html")
    if not backup_path.exists():
        import shutil
        shutil.copy2(filepath, backup_path)
        print(f"  バックアップ: {backup_path.name}")

    Path(filepath).write_text(result, 'utf-8')
    print(f"  CSS/JS置換完了: {rel}")
    return True


def validate(html, rel):
    """変換後の検証チェック"""
    warnings = []

    if 'class="rh"' not in html and '<header class="rh">' not in html:
        warnings.append("WARNING: header.rh が存在しません")

    if 'class="l1"' not in html:
        warnings.append("WARNING: section.l1 が存在しません")

    if 'class="boundary"' not in html:
        warnings.append("WARNING: .boundary が存在しません")

    sec3_count = html.count('class="sec3"')
    if sec3_count < 5:
        warnings.append(f"WARNING: .sec3 が{sec3_count}個しかありません (5個以上推奨)")

    if '<canvas' not in html:
        warnings.append("WARNING: <canvas> タグが存在しません（チャートが失われた可能性）")

    # 旧クラスの残存チェック
    old_classes = ['score-banner', 'score-section', 'score-big', 'div class="container"']
    for oc in old_classes:
        # Allow in template CSS (style blocks) but not in HTML body
        # Simple check: just look outside of style tags
        stripped = re.sub(r'<style>.*?</style>', '', html, flags=re.DOTALL)
        stripped = re.sub(r'<script>.*?</script>', '', stripped, flags=re.DOTALL)
        if oc in stripped:
            warnings.append(f"WARNING: 旧クラス '{oc}' がHTML本体に残っています")

    return warnings


def find_report_files():
    """変換対象のHTMLファイルを全て検出"""
    files = []
    for html_path in sorted(BASE_DIR.rglob('*.html')):
        rel = str(html_path.relative_to(BASE_DIR))

        # Non-report files
        if rel in NON_REPORT_FILES:
            continue

        # Skip files
        if rel in SKIP_FILES:
            continue

        # index.html files
        if html_path.name == 'index.html':
            continue

        # Must be in a ticker subdirectory (TICKER/QUARTER.html)
        parts = html_path.relative_to(BASE_DIR).parts
        if len(parts) < 2:
            continue

        # Skip non-ticker directories
        parent = parts[0]
        if parent in ('legal', 'logos', 'assets', '_old', 'node_modules'):
            continue

        files.append(str(html_path))

    return files


def main():
    args = sys.argv[1:]
    dry_run = '--dry-run' in args
    if dry_run:
        args.remove('--dry-run')

    if args:
        # 特定ファイル
        targets = []
        for a in args:
            p = BASE_DIR / a
            if p.exists():
                targets.append(str(p))
            else:
                print(f"ERROR: ファイルが見つかりません: {a}")
        if not targets:
            sys.exit(1)
    else:
        targets = find_report_files()

    print(f"対象ファイル数: {len(targets)}")
    if dry_run:
        print("モード: ドライラン（ファイル変更なし）")
    print()

    success = 0
    failed = 0
    skipped = 0

    for filepath in targets:
        rel = str(Path(filepath).relative_to(BASE_DIR))
        try:
            # Check if already new format
            content = Path(filepath).read_text('utf-8')
            if 'class="rh"' in content and 'class="l1"' in content and 'class="sec3"' in content:
                print(f"SKIP (既に新フォーマット): {rel}")
                skipped += 1
                continue

            result = migrate_html(filepath, dry_run)
            if result:
                success += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\nERROR: {rel}")
            print(f"  {e}")
            traceback.print_exc()
            failed += 1
            continue

    print(f"\n{'='*60}")
    print(f"完了: 成功={success}, 失敗={failed}, スキップ={skipped}")
    print(f"{'='*60}")

    if failed > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
