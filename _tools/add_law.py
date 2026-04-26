#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
add_law.py — Tự động thêm 1 bộ Luật mới vào LegalMap (Level 3)
═══════════════════════════════════════════════════════════════════

Usage:
  python3 add_law.py <source.doc|.docx|.pdf|.txt> [--no-kw]

Workflow:
  1. Convert source → text
  2. Detect Số hiệu / Tên Luật / Hiệu lực
  3. Detect Chương + Điều + nội dung
  4. Auto-extract keywords từ "Điều Giải thích từ ngữ"
  5. Auto-link điều ↔ từ khoá (content match)
  6. Generate legalmap/data/luat_NNN_YYYY.js
  7. Update legalmap/data/manifest.json
  8. (Optional) Auto commit + push dev

Author: cháu Claude (cho chú Phong)
"""
import os, re, sys, json, subprocess, argparse, hashlib
from pathlib import Path

REPO_ROOT = Path('/Users/nguyentanphong/Desktop/WEB - CÁC ĐƠN VỊ/Website-c-nh-n')
DATA_DIR = REPO_ROOT / 'legalmap' / 'data'
MANIFEST = DATA_DIR / 'manifest.json'

# ─── 6 màu brand mặc định cho Luật mới ───
COLOR_PALETTE = [
  ('red',    '#ED1C24', '🛒'),  # đỏ — TMĐT, kinh doanh
  ('blue',   '#1565c0', '🛡️'),  # xanh — an ninh
  ('purple', '#7B1FA2', '🔒'),  # tím — riêng tư, dữ liệu
  ('green',  '#2E7D32', '🌿'),  # xanh lá — môi trường, lao động
  ('orange', '#E65100', '⚖️'),  # cam — trách nhiệm, hình sự
  ('teal',   '#00695C', '💡'),  # xanh ngọc — đổi mới sáng tạo
]

ROMAN = {'I':1,'II':2,'III':3,'IV':4,'V':5,'VI':6,'VII':7,'VIII':8,'IX':9,'X':10,
        'XI':11,'XII':12,'XIII':13,'XIV':14,'XV':15}


def convert_to_text(src: Path) -> str:
    """Convert .doc/.docx/.pdf → text"""
    ext = src.suffix.lower()
    out = Path('/tmp') / (src.stem + '.txt')

    if ext == '.txt':
        return src.read_text(encoding='utf-8', errors='replace')
    if ext in ('.doc', '.docx'):
        subprocess.run(['textutil', '-convert', 'txt', '-output', str(out), str(src)], check=True)
        return out.read_text(encoding='utf-8', errors='replace')
    if ext == '.pdf':
        # macOS native: textutil cũng convert được pdf? thực ra không. dùng pdftotext nếu có
        if subprocess.run(['which', 'pdftotext'], capture_output=True).returncode == 0:
            subprocess.run(['pdftotext', '-layout', str(src), str(out)], check=True)
            return out.read_text(encoding='utf-8', errors='replace')
        raise RuntimeError("PDF cần cài pdftotext: brew install poppler")
    raise RuntimeError(f"Định dạng không hỗ trợ: {ext}")


def detect_meta(text: str) -> dict:
    """Detect số hiệu, tên Luật, hiệu lực"""
    meta = {}
    # Số hiệu: "Luật số: 91/2025/QH15"
    m = re.search(r'Luật\s+số\s*[:.]?\s*(\d+/\d+/QH\d+)', text)
    if not m:
        m = re.search(r'\b(\d{1,3}/\d{4}/QH\d+)\b', text)
    if m:
        meta['sohieu'] = m.group(1)
        n, y = m.group(1).split('/')[0], m.group(1).split('/')[1]
        meta['number'] = int(n)
        meta['year'] = int(y)
        meta['id'] = f"luat_{int(n):03d}_{y}"
        meta['slug'] = f"{int(n)}-{y}"

    # Tên Luật: dòng "LUẬT\nXXX" — XXX là tên đầy đủ
    m = re.search(r'^LUẬT\s*\n([^\n]+)', text, re.MULTILINE)
    if m:
        title_raw = m.group(1).strip()
        # Capitalize: "BẢO VỆ DỮ LIỆU CÁ NHÂN" → "Bảo vệ dữ liệu cá nhân"
        title = ' '.join(w.capitalize() if i == 0 else w.lower() for i, w in enumerate(title_raw.split()))
        meta['title'] = 'Luật ' + title

    # Hiệu lực: "có hiệu lực từ ngày 01 tháng 01 năm 2026" hoặc "Luật này có hiệu lực thi hành từ ngày..."
    m = re.search(r'có hiệu lực[^.\n]*ngày\s+(\d+)\s+tháng\s+(\d+)\s+năm\s+(\d+)', text, re.IGNORECASE)
    if m:
        d, mo, y = m.group(1).zfill(2), m.group(2).zfill(2), m.group(3)
        meta['hieuluc'] = f"{d}/{mo}/{y}"
    else:
        meta['hieuluc'] = '01/01/' + str(meta.get('year', 2026) + 1)  # fallback năm sau

    return meta


def detect_structure(text: str) -> tuple:
    """Detect Chương + Điều + nội dung"""
    lines = text.split('\n')

    ch_starts = []
    for i, l in enumerate(lines):
        m = re.match(r'^Chương\s+(I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII|XIII|XIV|XV)\s*$', l.strip())
        if m:
            title = lines[i+1].strip() if i+1 < len(lines) else ''
            ch_starts.append({
                'line': i,
                'roman': m.group(1),
                'num': ROMAN[m.group(1)],
                'title': title,
            })

    article_starts = []
    for i, l in enumerate(lines):
        m = re.match(r'^Điều\s+(\d+)\.\s*(.+)$', l.strip())
        if m:
            article_starts.append({
                'line': i,
                'n': int(m.group(1)),
                'name': m.group(2).strip(),
            })

    boundaries = sorted(set(
        [a['line'] for a in article_starts] +
        [c['line'] for c in ch_starts] +
        [len(lines)]
    ))

    articles = []
    for a in article_starts:
        next_b = next((b for b in boundaries if b > a['line']), len(lines))
        content = '\n'.join(lines[a['line']+1:next_b]).strip()
        ch = 1
        for c in ch_starts:
            if c['line'] < a['line']:
                ch = c['num']
        articles.append({'n':a['n'],'name':a['name'],'full':content,'ch':ch})

    # Compute chapter ranges
    ch_ranges = {}
    for a in articles:
        ch = a['ch']
        if ch not in ch_ranges:
            ch_ranges[ch] = {'from': a['n'], 'to': a['n']}
        else:
            ch_ranges[ch]['to'] = a['n']

    # Build CH list
    CH = []
    for c in ch_starts:
        n = c['num']
        rng = ch_ranges.get(n, {'from':0,'to':0})
        # Tạo label ngắn từ title (max 2-3 từ chính)
        words = c['title'].split()
        if len(words) <= 4:
            short = ' '.join(words)
        else:
            short = ' '.join(words[:3]) + '...'
        # Chuyển sang viết hoa chữ đầu
        short = short.title() if short.isupper() else short
        CH.append({
            'id': f'c{n}',
            'lbl': f'Ch.{c["roman"]}\n{short}',
            'from': rng['from'],
            'to': rng['to'],
            'desc': f'Chương {c["roman"]} — {c["title"]}\nĐiều {rng["from"]} đến Điều {rng["to"]}',
        })

    return CH, articles


def extract_kw_from_definitions(articles: list) -> list:
    """Trích keywords từ Điều 'Giải thích từ ngữ' (auto)"""
    KW = []
    used_ids = set()

    # Find Điều giải thích từ ngữ
    gt = next((a for a in articles if re.search(r'giải thích từ ngữ|định nghĩa', a['name'], re.IGNORECASE)), None)
    if not gt:
        return KW

    # Parse numbered list: "1. <Term> là <definition>...; 2. <Term2> là..."
    # Patterns:
    #   - "1. Dữ liệu cá nhân là dữ liệu số..."
    #   - "1. Hệ thống thông tin là tập hợp..."
    full = gt['full']

    # Split by numbered items
    items = re.split(r'\n(?=\d+\.\s+[A-ZẮÂÊÔƠƯĐÁÀẢÃẠÂẦẤẨẪẬĂẰẮẲẴẶÉÈẺẼẸÊỀẾỂỄỆÍÌỈĨỊÓÒỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÚÙỦŨỤƯỪỨỬỮỰÝỲỶỸỴ])', full)

    for it in items:
        m = re.match(r'^\d+\.\s+([^\n]+?)\s+là\s+([^\n]+)', it.strip())
        if not m:
            continue
        term_raw = m.group(1).strip()
        # Clean term: bỏ chữ thừa, lấy 2-3 từ chính
        term = term_raw

        # Generate id từ chữ cái đầu các từ
        words = re.sub(r'[^\w\sÀ-ỹ]', '', term).split()
        if len(words) >= 2:
            kid = 'k' + ''.join(w[0].upper() for w in words[:3])
        else:
            kid = 'k' + term[:3].upper().replace(' ', '')

        # Đảm bảo id duy nhất
        base = kid
        i = 2
        while kid in used_ids:
            kid = base + str(i); i += 1
        used_ids.add(kid)

        # Label 2 dòng (split nếu dài)
        if len(term) > 14:
            mid = len(term) // 2
            sp = term.find(' ', mid - 3)
            if sp > 0:
                lbl = term[:sp] + '\n' + term[sp+1:]
            else:
                lbl = term
        else:
            lbl = term

        # Type: kwc (concept) hoặc kwg (group). Heuristic: nếu term ngắn (< 4 từ) → kwc; nếu dài → kwg
        kw_type = 'kwc' if len(words) <= 3 else 'kwg'

        KW.append({
            'id': kid,
            'lbl': lbl,
            'type': kw_type,
            'terms': [term.lower()],  # base term, mở rộng sau
        })

    return KW


def find_keywords_in_content(content: str, KW: list) -> list:
    """Tìm keyword nào xuất hiện trong content"""
    matched = []
    cl = content.lower()
    for kw in KW:
        for term in kw.get('terms', []):
            if term and term.lower() in cl:
                matched.append(kw['id'])
                break
    return matched


def generate_js(meta: dict, CH: list, articles: list, KW: list, color_idx: int = None) -> str:
    """Generate luat_NNN_YYYY.js"""
    if color_idx is None:
        # Pick color based on hash để stable
        color_idx = int(hashlib.md5(meta['id'].encode()).hexdigest(), 16) % len(COLOR_PALETTE)
    variant, color, emoji = COLOR_PALETTE[color_idx]

    # Auto-link articles to keywords
    for a in articles:
        a['kw'] = find_keywords_in_content(a['full'], KW)

    out = []
    out.append('// ═══════════════════════════════════════════════════')
    out.append(f"// DATA MODULE — {meta['title']} {meta['sohieu']}")
    out.append('// LegalMap · Hướng Dương Edition')
    out.append('// Auto-generated by add_law.py')
    out.append('// ═══════════════════════════════════════════════════')
    out.append('')
    out.append('window.LUAT_REGISTRY = window.LUAT_REGISTRY || {};')
    out.append(f"window.LUAT_REGISTRY['{meta['id']}'] = {{")
    out.append('')
    out.append('  meta: {')
    out.append(f"    id:      '{meta['id']}',")
    out.append(f"    title:   '{meta['title']}',")
    out.append(f"    sohieu:  '{meta['sohieu']}',")
    out.append(f"    chuong:  {len(CH)},")
    out.append(f"    dieu:    {len(articles)},")
    out.append(f"    hieuluc: '{meta['hieuluc']}',")
    out.append(f"    color:   '{color}',")
    out.append(f"    colorCh: '{color}',")
    out.append(f"    colorD:  '{color}',")
    out.append('  },')
    out.append('')

    # CH
    out.append('CH:[')
    for c in CH:
        lbl = c['lbl'].replace("\n","\\n").replace("'","\\'")
        desc = c['desc'].replace("\n","\\n").replace("'","\\'")
        out.append(f"  {{id:'{c['id']}',lbl:'{lbl}',from:{c['from']},to:{c['to']},")
        out.append(f"   desc:'{desc}'}},")
    out.append('],')
    out.append('')

    # DD
    out.append('DD:[')
    for a in articles:
        name = a['name'].replace("'","\\'")
        full = a['full'].replace("`","'")
        kw_str = ','.join(f"'{k}'" for k in a['kw'])
        out.append(f"{{n:{a['n']},name:'{name}',kw:[{kw_str}],")
        out.append(f"full:`{full}`}},")
        out.append('')
    out.append('],')
    out.append('')

    # KW
    out.append('KW:[')
    for k in KW:
        lbl = k['lbl'].replace("\n","\\n").replace("'","\\'")
        terms = "','".join(t.replace("'","\\'") for t in k['terms'])
        out.append(f"  {{id:'{k['id']}',  lbl:'{lbl}', type:'{k['type']}',")
        out.append(f"   terms:['{terms}']}},")
    out.append('],')
    out.append('')

    out.append('NOKW_SET: new Set([]),')
    out.append('')
    out.append('};')

    return '\n'.join(out), variant, color, emoji


def update_vercel_rewrite(slug: str):
    """Add rewrite rule for /legalmap/{slug} → viewer.html"""
    vp = REPO_ROOT / 'vercel.json'
    cfg = json.loads(vp.read_text())
    rule = { "source": f"/legalmap/{slug}", "destination": "/legalmap/viewer" }
    rewrites = cfg.setdefault('rewrites', [])
    if any(r.get('source') == rule['source'] for r in rewrites):
        print(f"  ⚠️  Rewrite cho /legalmap/{slug} đã có — skip")
        return
    rewrites.append(rule)
    vp.write_text(json.dumps(cfg, ensure_ascii=False, indent=2))
    print(f"  ✅ Đã thêm rewrite vercel.json: /legalmap/{slug}")


def update_manifest(meta: dict, CH: list, DD: list, KW: list, variant: str, color: str, emoji: str):
    """Add law entry to manifest.json"""
    mf = json.loads(MANIFEST.read_text())
    # Skip if already exists
    if any(l['id'] == meta['id'] for l in mf['laws']):
        print(f"  ⚠️  {meta['id']} đã có trong manifest — skip")
        return
    mf['laws'].append({
        'id': meta['id'],
        'slug': meta['slug'],
        'file': f"data/{meta['id']}.js",
        'title': meta['title'],
        'sohieu': meta['sohieu'],
        'chuong': len(CH),
        'dieu': len(DD),
        'kw': len(KW),
        'hieuluc': meta['hieuluc'],
        'color': color,
        'variant': variant,
        'tagEmoji': emoji,
        'tagText': meta['title'].replace('Luật ', ''),
        'pitch': f"Bản đồ tương tác {meta['title']} — {len(CH)} chương · {len(DD)} điều · {len(KW)} từ khoá liên kết.",
    })
    mf['updated'] = '2026-04-26'
    MANIFEST.write_text(json.dumps(mf, ensure_ascii=False, indent=2))
    print(f"  ✅ Đã thêm vào manifest.json")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', help='Đường dẫn file .doc/.docx/.pdf/.txt')
    parser.add_argument('--no-kw', action='store_true', help='Bỏ qua auto KW từ Giải thích từ ngữ')
    parser.add_argument('--color', type=int, help='Index màu palette (0-5)')
    args = parser.parse_args()

    src = Path(args.source).expanduser()
    if not src.exists():
        print(f"❌ Không tìm thấy: {src}")
        sys.exit(1)

    print(f"📄 Source: {src.name}")
    print('🔄 Convert → text...')
    text = convert_to_text(src)
    print(f"   text size: {len(text)} chars")

    print('🔍 Detect meta...')
    meta = detect_meta(text)
    print(f"   ID: {meta.get('id')}")
    print(f"   Title: {meta.get('title')}")
    print(f"   Số hiệu: {meta.get('sohieu')}")
    print(f"   Hiệu lực: {meta.get('hieuluc')}")

    if not all(k in meta for k in ['id','title','sohieu']):
        print("❌ Không detect đủ meta. Hãy bổ sung tay.")
        sys.exit(1)

    print('🔍 Detect Chương + Điều...')
    CH, articles = detect_structure(text)
    print(f"   Chương: {len(CH)} | Điều: {len(articles)}")

    if args.no_kw:
        KW = []
        print('⚠️  Bỏ qua auto KW (--no-kw)')
    else:
        print('🏷️  Auto-extract keywords từ Giải thích từ ngữ...')
        KW = extract_kw_from_definitions(articles)
        print(f"   Tìm được {len(KW)} keywords từ định nghĩa")

    print('💾 Generate JS file...')
    js_content, variant, color, emoji = generate_js(meta, CH, articles, KW, args.color)
    out_path = DATA_DIR / f"{meta['id']}.js"
    out_path.write_text(js_content)
    print(f"   ✅ {out_path.name} — {out_path.stat().st_size} bytes")

    print('📝 Update manifest...')
    update_manifest(meta, CH, articles, KW, variant, color, emoji)

    print('🔁 Update vercel.json rewrite...')
    update_vercel_rewrite(meta['slug'])

    print('')
    print('═══════════════════════════════════════════════════')
    print(f"✅ HOÀN TẤT — {meta['title']}")
    print(f"   File: legalmap/data/{meta['id']}.js")
    print(f"   URL local: http://localhost:8765/legalmap")
    print(f"   URL prod:  https://www.nguyentanphong.com/legalmap/{meta['slug']}")
    print(f"   Stats:    {len(CH)} chương · {len(articles)} điều · {len(KW)} từ khoá")
    print('═══════════════════════════════════════════════════')
    print('')
    print('🔜 Tiếp theo:')
    print('   1. cd "WEB - CÁC ĐƠN VỊ/Website-c-nh-n"')
    print('   2. git add legalmap/data/')
    print(f"   3. git commit -m \"feat(legalmap): thêm {meta['title']}\"")
    print('   4. git push origin dev && git checkout main && git merge dev && git push origin main')


if __name__ == '__main__':
    main()
