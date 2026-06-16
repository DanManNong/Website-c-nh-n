# -*- coding: utf-8 -*-
import re, sys

# ---- VietnamNet (bài mới, làm spotlight) ----
VN_URL = "https://vietnamnet.vn/den-luc-thi-truong-sang-tao-noi-dung-can-buoc-ra-khoi-vung-xam-tu-phat-2524168.html"
VN_IMG = "https://static-images.vnncdn.net/vps_images_publish/000001/000003/2026/6/9/nguyentanphong-1349.png?width=0&amp;s=kOJGBtGtSLGY1UvW3eTDmw"
VN_TITLE = "Đến lúc thị trường sáng tạo nội dung cần bước ra khỏi vùng xám tự phát"
VN_META = "VietNamNet · 09/06/2026"

# ---- Công Thương (bài cũ, hạ xuống card marquee) ----
CT_URL = "https://congthuong.vn/thuong-mai-dien-tu-muon-phat-trien-ben-vung-phai-manh-tay-voi-hang-gia-458214.html"
CT_IMG = "https://cdn-i2.congthuong.vn/upload/2026/05/26/z78662422599334dd16bfc96a27c29f5e8e05943f6a445-09404299.jpg"
CT_TITLE = "Thương mại điện tử muốn phát triển bền vững phải mạnh tay với hàng giả"
CT_EXCERPT = "Phỏng vấn Phó Chủ tịch VECOM Nguyễn Tấn Phong: chỉ rõ bốn kẽ hở pháp lý và đề xuất liên thông dữ liệu, AI, blockchain để siết hàng giả trên môi trường số."

L = {
 "index.html": {
   "eyebrow":"Mới nhất · Phỏng vấn",
   "summary":"Trao đổi trên VietNamNet, ông Nguyễn Tấn Phong — Phó Chủ tịch Hiệp hội Thương mại điện tử Việt Nam (VECOM) — cho rằng thị trường sáng tạo nội dung đã đến lúc bước ra khỏi “vùng xám” tự phát để vận hành minh bạch, chuyên nghiệp. Khi các luật mới về an ninh mạng và thương mại điện tử có hiệu lực từ 01/7/2026, KOL và nhà sáng tạo buộc phải nâng chuẩn trách nhiệm với nội dung và quảng cáo của mình.",
   "cta":"Đọc toàn văn trên VietNamNet →",
   "ct_tag":"Hàng giả","ct_more":"Đọc tiếp →",
 },
 "en.html": {
   "eyebrow":"Latest · Interview",
   "summary":"Speaking to VietNamNet, Mr. Nguyen Tan Phong — Vice President of the Vietnam E-commerce Association (VECOM) — argues that the content-creation market must step out of its self-styled “grey zone” toward transparency and professionalism. As new cybersecurity and e-commerce laws take effect from 1 July 2026, KOLs and creators will be held to far higher standards for the content and advertising they publish.",
   "cta":"Read the full article on VietNamNet →",
   "ct_tag":"Counterfeit Goods","ct_more":"Read more →",
 },
 "ja.html": {
   "eyebrow":"最新 · インタビュー",
   "summary":"VietNamNet紙で、ベトナム電子商取引協会（VECOM）副会長のグエン・タン・フォン氏は、コンテンツ制作市場は自然発生的な「グレーゾーン」から抜け出し、透明性とプロ意識を備えて運営される時期に来ていると指摘した。2026年7月1日からサイバーセキュリティと電子商取引に関する新法が施行されると、KOLやクリエイターは自らのコンテンツと広告に対してより高い責任基準が求められる。",
   "cta":"VietNamNetで全文を読む →",
   "ct_tag":"Counterfeit Goods","ct_more":"続きを読む →",
 },
 "zh.html": {
   "eyebrow":"最新 · 专访",
   "summary":"在《VietNamNet》的访谈中，越南电子商务协会（VECOM）副会长阮晋峰认为，内容创作市场已到了走出自发“灰色地带”、迈向透明与专业化运营的时候。随着网络安全和电子商务新法将于2026年7月1日生效，KOL和创作者必须对自己发布的内容和广告承担更高的责任标准。",
   "cta":"在《VietNamNet》阅读全文 →",
   "ct_tag":"Counterfeit Goods","ct_more":"阅读更多 →",
 },
}

def spotlight_block(cfg):
    return (
f'''<a href="{VN_URL}" target="_blank" class="article-spotlight" aria-label="{VN_TITLE}">
      <img class="spotlight-media" src="{VN_IMG}" alt="{VN_TITLE}" loading="lazy">
      <span class="spotlight-body">
        <span class="spotlight-eyebrow">{cfg["eyebrow"]}</span>
        <span class="spotlight-title">{VN_TITLE}</span>
        <span class="spotlight-meta">{VN_META}</span>
        <span class="spotlight-summary">{cfg["summary"]}</span>
        <span class="spotlight-cta">{cfg["cta"]}</span>
      </span>
    </a>
''')

def ct_card(cfg):
    return (
f'''        <a href="{CT_URL}" target="_blank" class="article-card">
          <div class="article-thumb article-thumb-img" style="background-image:url('{CT_IMG}');">
            <span class="article-tag">{cfg["ct_tag"]}</span>
          </div>
          <div class="article-body">
            <div class="article-meta">Báo Công Thương · 2026</div>
            <h3 class="article-title">{CT_TITLE}</h3>
            <p class="article-excerpt">{CT_EXCERPT}</p>
            <span class="article-more">{cfg["ct_more"]}</span>
          </div>
        </a>
''')

VN_PRESS = ("""        vietnamnet: {
          name: 'VietNamNet',
          articles: [
            { title: '%s', url: '%s' }
          ]
        },
""" % (VN_TITLE, VN_URL))

for fn, cfg in L.items():
    s = open(fn, encoding="utf-8").read()
    rep = []

    # 1) Thay spotlight: Công Thương -> VietnamNet (match cả khối <a class=article-spotlight>)
    if VN_URL in s and "article-spotlight" in s and CT_URL not in s.split("articles-marquee")[0]:
        rep.append("spotlight đã là VNN?")
    pat = re.compile(r'<a href="https://congthuong\.vn/thuong-mai-dien-tu[^"]*" target="_blank" class="article-spotlight".*?</a>\n', re.DOTALL)
    s2, n = pat.subn(spotlight_block(cfg), s)
    if n == 1:
        s = s2; rep.append("spotlight->VNN")
    else:
        print(f"{fn} ❌ không match spotlight Công Thương (n={n})"); sys.exit(1)

    # 2) Chèn Công Thương thành card marquee đầu tiên
    anchor = '      <div class="articles-marquee-track">\n'
    if CT_URL in s.split('articles-marquee-track')[1][:4000]:
        rep.append("CT card đã có?")
    if anchor in s:
        s = s.replace(anchor, anchor + ct_card(cfg), 1); rep.append("CT->card")
    else:
        print(f"{fn} ❌ không thấy marquee-track anchor"); sys.exit(1)

    # 3) keyframe ×7 -> ×8
    a = s.count("(320px + 20px) * 7)"); b = s.count("(260px + 14px) * 7)")
    s = s.replace("(320px + 20px) * 7)", "(320px + 20px) * 8)").replace("(260px + 14px) * 7)", "(260px + 14px) * 8)")
    rep.append(f"keyframe×8({a}+{b})")

    # 4) Z07 PRESS_DATA: thêm vietnamnet trước congthuong
    ct_press_anchor = "        congthuong: {"
    if "vietnamnet: {" in s:
        rep.append("press VNN đã có")
    elif ct_press_anchor in s:
        s = s.replace(ct_press_anchor, VN_PRESS + ct_press_anchor, 1); rep.append("press+VNN")
    else:
        rep.append("⚠ ko thấy congthuong press")

    # 5) Z07 logo buttons (2 hàng: visible + aria-hidden)
    vis_anchor = """<button type="button" class="press-logo" onclick="openPressModal('vnexpress')">VnExpress</button>"""
    hid_anchor = """<button type="button" class="press-logo" onclick="openPressModal('vnexpress')" aria-hidden="true" tabindex="-1">VnExpress</button>"""
    vis_new = vis_anchor + """\n        <button type="button" class="press-logo" onclick="openPressModal('vietnamnet')">VietNamNet</button>"""
    hid_new = hid_anchor + """\n        <button type="button" class="press-logo" onclick="openPressModal('vietnamnet')" aria-hidden="true" tabindex="-1">VietNamNet</button>"""
    if "openPressModal('vietnamnet')" in s:
        rep.append("logo VNN đã có")
    else:
        c1 = 1 if vis_anchor in s else 0
        if c1: s = s.replace(vis_anchor, vis_new, 1)
        c2 = 1 if hid_anchor in s else 0
        if c2: s = s.replace(hid_anchor, hid_new, 1)
        rep.append(f"logo+VNN({c1}+{c2})")

    # 6) schema sameAs += VietnamNet
    ct_sameas = '    "https://congthuong.vn/thuong-mai-dien-tu-muon-phat-trien-ben-vung-phai-manh-tay-voi-hang-gia-458214.html",'
    if ('    "%s",' % VN_URL) in s:
        rep.append("sameAs đã có")
    elif ct_sameas in s:
        s = s.replace(ct_sameas, ct_sameas + '\n    "%s",' % VN_URL, 1); rep.append("sameAs+VNN")
    else:
        rep.append("⚠ ko thấy sameAs CT")

    open(fn, "w", encoding="utf-8").write(s)
    print(f"{fn} ✅ " + "; ".join(rep))
