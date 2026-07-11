# -*- coding: utf-8 -*-
"""GEO upgrade: bổ sung schema Person (description/knowsAbout/worksFor) cho 4 file ngôn ngữ."""
import sys

# knowsAbout: thuật ngữ định vị chuyên môn (theo tài liệu GEO)
KNOWS_VI = ["Kinh tế số","Thương mại điện tử","An ninh mạng","Trọng tài thương mại",
            "Luật Giao dịch điện tử 2023","Nghị định 13/2023/NĐ-CP","Bảo vệ dữ liệu cá nhân",
            "Xuất khẩu số","Tự động hoá kinh doanh","Pháp lý livestream và KOL"]
KNOWS_EN = ["Digital Economy","E-commerce","Cybersecurity","Commercial Arbitration",
            "Vietnam Law on Electronic Transactions 2023","Decree 13/2023/ND-CP","Personal Data Protection",
            "Digital Export","Business Automation","Livestream & KOL Legal Compliance"]

WORKSFOR = '''  "worksFor": [
    { "@type": "Organization", "name": "Hiệp hội Thương mại điện tử Việt Nam", "alternateName": "VECOM", "url": "https://vecom.vn" },
    { "@type": "Organization", "name": "Trung tâm Tư vấn Pháp luật - Hiệp hội Thương mại điện tử Việt Nam" }
  ],'''

DESC = {
 "index.html": "Luật gia, Trọng tài viên thương mại, Phó Chủ tịch Hiệp hội Thương mại điện tử Việt Nam (VECOM), chuyên gia tư vấn chiến lược Thương mại điện tử, An ninh mạng và Tự động hoá kinh doanh.",
 "en.html": "Jurist, commercial arbitrator, Vice President of the Vietnam E-commerce Association (VECOM), strategic consultant in e-commerce, cybersecurity and business automation.",
 "ja.html": "法学者・商事仲裁人。ベトナム電子商取引協会（VECOM）副会長。EC戦略、サイバーセキュリティ、業務自動化のコンサルタント。",
 "zh.html": "法学专家、商事仲裁员，越南电子商务协会（VECOM）副会长，专注电子商务战略、网络安全与业务自动化咨询。",
}

ANCHOR = {
 "index.html": '  "jobTitle": "Phó Chủ tịch Hiệp hội Thương mại điện tử Việt Nam (VECOM)",',
 "en.html":    '  "jobTitle": "Vice President of the Vietnam E-commerce Association (VECOM)",',
 "ja.html":    '  "jobTitle": "ベトナム電子商取引協会(VECOM)副会長",',
 "zh.html":    '  "jobTitle": "越南电子商务协会(VECOM)副会长",',
}

for fn in ["index.html","en.html","ja.html","zh.html"]:
    s = open(fn, encoding="utf-8").read()
    if '"knowsAbout"' in s:
        print(f"{fn} ⏭ đã có knowsAbout"); continue
    knows = KNOWS_VI if fn=="index.html" else KNOWS_EN
    knows_json = '  "knowsAbout": [' + ", ".join(f'"{k}"' for k in knows) + '],'
    block = (ANCHOR[fn] + "\n"
             + f'  "description": "{DESC[fn]}",\n'
             + knows_json + "\n"
             + WORKSFOR)
    if ANCHOR[fn] not in s:
        print(f"{fn} ❌ không thấy anchor jobTitle"); sys.exit(1)
    s = s.replace(ANCHOR[fn], block, 1)
    open(fn,"w",encoding="utf-8").write(s)
    print(f"{fn} ✅ +description +knowsAbout({len(knows)}) +worksFor")
