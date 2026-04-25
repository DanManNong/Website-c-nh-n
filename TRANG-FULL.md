# 👤 TRANG FULL — `preview-full.html` (offline backup)

> File HTML: `preview-full.html`
> URL: `/preview-full` đã 308 → `/` (không hiển thị public)
> Mục đích: Trang Cá Nhân đầy đủ với 14 zones · backup cho khi cần show full profile
> Cập nhật: 25/04/2026

---

## 🎯 Mục đích

- Trang giới thiệu chuyên gia ĐẦY ĐỦ (vs Card đơn giản)
- 14 zone content: từ hero · stats · vai trò · báo chí · thư viện · liên hệ · footer
- Hiện đang **ẨN** trên production (`.vercelignore` chặn? KHÔNG — file vẫn deploy nhưng URL redirect về `/`)
- Khi chú muốn dùng full version: chỉ cần `cp preview-full.html index.html` + xoá noindex + redeploy

---

## 📐 Cấu trúc HTML — 14 ZONES

```
┌──────────────────────────────────────────┐
│ <head>                                   │
│   - SEO meta · Schema.org Person          │
│   - GA4 · Manifest · OG · Twitter        │
│   - meta robots: noindex (không cho crawl)│
│ </head>                                  │
│                                          │
│ <body>                                   │
│   ┌─ Sidebar fixed right ──────────┐    │
│   │ (Tab Danh Thiếp/Trang CN ẨN)   │    │
│   │ [💬 Zalo · 64×64 · blink]      │    │
│   │ [📞 Phone · 64×64 · blink]     │    │
│   │ [📘 Lưu DB · 64×64 · gold]    │    │
│   └─────────────────────────────────┘    │
│                                          │
│   Z01 · Language Bar (đã xoá HTML)       │
│   Z02 · Nav Pills static · sticky top    │
│   Z03 · Hero (2 cột web · stack mobile)  │
│   Z04 · Stats (4 chỉ số)                 │
│   Z05 · 6 Tổ chức đồng hành              │
│   Z06 · Articles Marquee 5 bài chậm      │
│   Z07 · Báo chí Marquee 7 logo + popup   │
│   Z08 · Thư viện 8 chuyên đề + view all  │
│   Z09 · Tài liệu + counter 6,875         │
│   Z10 · Manifesto đầy đủ (container)     │
│   Z11 · 5 Lĩnh vực + popup hashtag       │
│   Z12 · Lead Magnet bìa sách + form      │
│   Z13 · Liên hệ 6 kênh + Lưu DB         │
│   Z14 · Footer chữ ký + ©                │
│ </body>                                  │
└──────────────────────────────────────────┘
```

---

## 📋 14 ZONES — Chi tiết

### Z01 · Language Bar (ĐÃ XOÁ HTML)
- Trước: VN · EN · CN · KR · JP buttons
- Hiện tại: bỏ hoàn toàn

### Z02 · Nav Pills (sticky top, static center)
| Pill | Anchor | Icon |
|---|---|---|
| Góc Nhìn | `#Z06` | newspaper |
| Thư Viện | `#Z08` | book |
| Tài Liệu | `#Z09` | folder |
| Về Tôi | `#Z10` | user |
| Liên Hệ | `#Z13` | phone |

- Smooth scroll · scroll-margin 80px
- Mobile: nowrap · overflow-x scroll · swipe ngang

### Z03 · Hero (Khối giữa)
**Desktop (≥900px):** 2 cột grid
- Trái: tagline + tên + 4 titles + bio
- Phải: avatar 360px tròn

**Mobile:** stack
- Tagline lên đầu
- Avatar 160px
- Tên + titles + bio

**Bio nháp** (~50 chữ): Với hơn 10 năm đồng hành cùng doanh nghiệp trong lĩnh vực Kinh tế số và Pháp luật, tôi tập trung tư vấn chiến lược TMĐT và hệ thống Tự động hoá kinh doanh — giúp các đơn vị vận hành hiệu quả, an toàn pháp lý, sẵn sàng mở rộng quốc tế.

### Z04 · Stats (4 chỉ số)
| Số | Label |
|---|---|
| 10+ | Năm Kinh Nghiệm |
| 05 | Vai Trò Chuyên Môn |
| 100+ | **Bài Viết Chuyên Đề** |
| 6,875 | Đối Tác Kết Nối |

### Z05 · Vai Trò Chuyên Môn — 6 tổ chức
| # | Tên | Link | Vai trò |
|---|---|---|---|
| 1 | **VECOM** | vecom.vn | Ủy viên BCH · Trưởng Ban Kiểm Tra · Trưởng đại diện phía Nam |
| 2 | **CLEAD** | clead.vn | Giám đốc TT Tư vấn Pháp luật, Hiệp hội TMĐT VN |
| 3 | **ARI** | ari.org.vn | Luật gia · Phó Viện Trưởng Viện KH Pháp lý Trọng tài |
| 4 | **TRACENT** | tracent.com.vn | Trọng tài viên · TT Trọng tài Thương mại TP.HCM |
| 5 | **EAGLE** | eagleacademy.vn | Giảng viên Cao cấp · BĐS · Quản trị DN |
| 6 | **HSGA** | hsga.vn/0915159499 | Hội Cựu Sinh viên Đại học Hoa Sen |

### Z06 · Góc Nhìn — 5 bài thật (marquee chậm 80s)
| # | Báo | Tag | Tên bài |
|---|---|---|---|
| 1 | NLD 2026 | Kinh tế số | Trách nhiệm pháp lý của sàn TMĐT và KOL |
| 2 | VnExpress | Bất động sản | Nhận diện rủi ro pháp lý địa ốc 2026 |
| 3 | NLD 2025 | An ninh mạng | Bảo vệ dữ liệu cá nhân trên không gian số |
| 4 | NLD 2025 | Livestream | Chấn chỉnh livestream bán hàng |
| 5 | Tuổi Trẻ 2025 | Hàng giả | Xử lý hàng giả: mới đến chợ đã bị theo dõi |

- Ảnh nháp picsum.photos (chú thay sau)
- Cards 320px · gap 20px · animation 80s

### Z07 · Báo chí — 7 báo (marquee 20s · click popup)
| Báo | Số bài (popup) |
|---|---|
| Người Lao Động | 5 |
| VnExpress | 3 |
| Tuổi Trẻ · Thanh Niên · Tiền Phong · PLO · Công Thương | 1 mỗi báo |

- Click logo → `openPressModal(key)` → modal hiển thị danh sách bài
- Modal style: gold border + numbered list

### Z08 · Thư Viện — 8 chuyên đề
**Unlock (4):**
- Cẩm nang Thương mại điện tử 2026
- Pháp lý Livestream
- Trọng tài thương mại
- Tự động hoá kinh doanh

**Locked (4):**
- Bảo vệ thương hiệu số
- An ninh mạng cho SME
- Hợp đồng điện tử
- Bất động sản & Đầu tư pháp lý

+ Link "Xem tất cả danh sách →"

### Z09 · Tài Liệu
- Counter "00006875" · Đối tác kết nối
- Nút "Tải về ngay" → password gate
- Nút "Đăng ký mới" → register modal

### Z10 · Manifesto (Tuyên Ngôn Thương Hiệu đầy đủ)
- Container box (rgba 0.35 + border gold)
- Eyebrow: "Tuyên Ngôn Thương Hiệu"
- Title: "Tôi tin điều gì — và tôi không tin điều gì"
- Quote north star italic gold center
- 7 đoạn paragraphs (3 đoạn "Tôi tin rằng" + 3 đoạn "Tôi không tin" + 1 đoạn phục vụ 3 nhóm)
- Signature: "— Nguyễn Tấn Phong"
- Format đơn giản (text plain, không bold/em)

### Z11 · Lĩnh vực trọng tâm — 5 categories + popup hashtag
| Category | Hashtags lọc |
|---|---|
| Kinh tế số & TMĐT | #tmdt · #livestream · #hopdong · #ocop · #dropship |
| Bất động sản | #bds · #dautu · #daugia |
| An ninh mạng | #anm · #sme |
| Trọng tài thương mại | #trongtai |
| Pháp luật & Quản trị | #phapluat · #quantri · #thue · #hanggia · #so |

- Click button → `openCatModal(key)`
- Modal hiện danh sách 20 bài nháp filter theo hashtags
- Hashtag matching highlight gold (background #E0AA79 navy text)

### Z12 · Lead Magnet — Cẩm nang 2026
- Bìa sách v2: img picsum.photos overlay gold + badge NHÁP đỏ
- Form 3 field: Họ tên · Email · SĐT (optional)
- Email validation strict + typo domain check (gmial/yhaoo/hotnail)
- Submit → lưu `localStorage.leadSubmissions` + GA `lead_submit`
- Hiện success card "Đăng ký thành công · email đã ghi nhận"
- Chú xem submissions qua `/admin` (offline)

### Z13 · Liên hệ
- 6 contact items: Hotline · Email · Zalo · Facebook · YouTube · LinkedIn
- Nút Lưu Danh Bạ gold gradient → vCard 3.0
- (Bộ 4 ô ngôn ngữ đã xoá)

### Z14 · Footer
- Signature 140px (filter brightness invert white)
- © NGUYEN TAN PHONG. ALL RIGHTS RESERVED.

---

## 🎨 CSS Highlights

### Design tokens
Same as Trang Danh Thiếp (gold/navy/cream)

### Custom animations
- `fadeUp` 1.2s
- `vBlink` 2.2s — Zalo/Phone/Save sidebar
- Articles marquee 80s
- Press marquee 20s

### Sticky elements
- Z02 nav pills sticky top z-index 900

### Modals
- `.press-modal-overlay` — Z07 popup
- `#catModal` — Z11 popup hashtag
- `#leadForm` success state — Z12

---

## 💻 JavaScript Functions

| Function | Mô tả |
|---|---|
| `saveContactFull()` | vCard cho Z13 button |
| `openPressModal(key)` | Z07 — show báo bài list |
| `closePressModal()` | Z07 — đóng |
| `openCatModal(key)` | Z11 — show category articles |
| `closeCatModal()` | Z11 — đóng |
| `openGate(item)` | Z08 — password gate (placeholder) |
| `openRegister()` | Z09 — register modal (placeholder) |
| `openQRModal()` | M-QR — danh thiếp modal |
| `changeLang(btn)` | (legacy Z01 - đã xoá HTML) |
| `trackEvent(name, params)` | GA4 wrapper |
| Dev mode toggle | URL param `?dev=1` → body.dev-mode → hiện grid + Zxx labels |

### Data objects (hardcoded)
```js
PRESS_DATA = { nld: {...}, vnexpress: {...}, ... }   // 7 báo + bài
ARTICLES_POOL = [ {id, title, tags}, ... ]          // 20 bài nháp
CAT_MAP = { tmdt: {...}, bds: {...}, ... }           // 5 categories
```

---

## 🌐 SEO

- **noindex, nofollow** (vì đã 308 → /)
- Title: "[PREVIEW · FULL v3] Nguyễn Tấn Phong" (legacy, không hiển thị do redirect)
- Schema.org Person + Affiliation 6 organizations
- Canonical URL `/`

---

## 📂 Files liên quan

| File | Quan hệ |
|---|---|
| `preview-full.html` | File chính (~99KB) |
| `index.html` | KHÁC file này (giờ là Card đơn giản) |
| Backup branch | `backup/v3-full-active` (snapshot v6.1.2) |
| Backup tag | `v3-full-backup` |

---

## 🚀 Cách kích hoạt full version (khi cần)

### Cách 1 — Replace `/` thành full
```bash
cp preview-full.html index.html
sed -i '' '/<meta name="robots" content="noindex/d' index.html
# Update title nếu cần
git add . && git commit -m "switch / sang full version" && git push
```

### Cách 2 — Tạo route riêng
```json
// vercel.json — bỏ redirect /preview-full → /
"redirects": [
  // remove: { "source": "/preview-full", ... }
]
```

### Cách 3 — Restore từ git tag
```bash
git show v3-full-backup:wireframe_nguyentanphong_v3.html > preview-full.html
```

---

## 🎯 Roadmap nâng cấp

### Cần content thật
- [ ] Z03 Bio: chú duyệt/sửa text
- [ ] Z05 HSGA: bổ sung mô tả chính xác
- [ ] Z06: thay 5 ảnh picsum bằng ảnh thật
- [ ] Z07: thay logo text bằng logo hình 7 báo
- [ ] Z08: nội dung 8 chuyên đề + file PDF tải về
- [ ] Z11: thay 20 bài demo bằng nội dung thật
- [ ] Z12: thiết kế bìa sách Cẩm nang thật

### Cần backend
- [ ] Z12 form submit → Mailchimp/Brevo (thay localStorage)
- [ ] Z08/Z09 password gate → real auth + content delivery
- [ ] Z11 articles → CMS (Sanity/Contentful)

### Cần thiết kế
- [ ] Case study section (Tier 2 add)
- [ ] Testimonials carousel
- [ ] Pricing/Services page

---

## 📊 Snapshot performance

| Chỉ số | Giá trị |
|---|---|
| HTML size | ~99KB (nhiều CSS + JS inline) |
| Total assets | ~140KB images + CDN fonts |
| Tổng load | ~400KB (gzip ~150KB) |
| Lighthouse Performance | 85+ (chưa optimize aggressive) |

---

*File mô tả · cập nhật khi có thay đổi cấu trúc.*
