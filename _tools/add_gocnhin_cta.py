# -*- coding: utf-8 -*-
"""Chèn nút CTA 'Xem Góc nhìn chuyên gia' vào cuối Z06 (sau dải marquee) cho 4 file."""
LABEL = {
 "index.html": "Đọc Góc nhìn chuyên gia — phân tích chuyên sâu →",
 "en.html": "Read expert analyses — Góc nhìn (Vietnamese) →",
 "ja.html": "専門家の分析記事を読む（ベトナム語）→",
 "zh.html": "阅读专家深度分析（越南语）→",
}
# anchor: mở khối <style> của marquee, nằm ngay sau </div></div> đóng marquee
ANCHOR = "    <style>\n      .articles-marquee {"

def cta(label):
    return ('    <div style="text-align:center;margin-top:26px;">\n'
            '      <a href="/goc-nhin" style="display:inline-block;background:linear-gradient(135deg,var(--gold),var(--gold-light));'
            'color:var(--navy);font-weight:700;font-size:13.5px;padding:12px 26px;border-radius:10px;text-decoration:none;'
            'box-shadow:0 8px 22px rgba(224,170,121,0.28);">' + label + '</a>\n'
            '    </div>\n')

for fn, label in LABEL.items():
    s = open(fn, encoding="utf-8").read()
    if 'href="/goc-nhin"' in s:
        print(f"{fn} ⏭ đã có CTA"); continue
    if ANCHOR not in s:
        print(f"{fn} ❌ không thấy anchor"); continue
    s = s.replace(ANCHOR, cta(label) + ANCHOR, 1)
    open(fn, "w", encoding="utf-8").write(s)
    print(f"{fn} ✅ chèn CTA")
