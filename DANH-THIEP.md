# 🪪 TRANG DANH THIẾP — `/` (production)

> File HTML: `coming-soon.html` (= `index.html`)
> URL chính thức: **https://www.nguyentanphong.com**
> Mục đích: Card điện tử thay thế danh thiếp giấy · share QR · gọi/Zalo nhanh
> Cập nhật: 25/04/2026

---

## 🎯 Mục đích

- Thay thế danh thiếp giấy bằng trang web 1 màn hình
- User scan QR → vào nguyentanphong.com → lưu liên hệ + nhắn Zalo + gọi
- Chỉ tiếng Việt (audience chính trong nước)
- Tối giản · load nhanh · không cuộn nhiều

---

## 📐 Cấu trúc HTML (top → bottom)

```
┌─────────────────────────────────────────┐
│ <head>                                   │
│   - Title, meta description, keywords    │
│   - Canonical, OG, Twitter Card          │
│   - Favicon, manifest, theme-color       │
│   - Schema.org Person + ContactPoint     │
│   - Preload avatar, preconnect CDN       │
│   - Google Analytics 4 (G-V45VVRDW8T)    │
│ </head>                                  │
│                                          │
│ <body>                                   │
│   ┌─ Sidebar fixed right ──────────┐    │
│   │ [💬 Zalo] [📞 Phone]            │    │
│   │ (32×32px · blink animation)     │    │
│   └─────────────────────────────────┘    │
│                                          │
│   ┌─ Lang switcher fixed top-right ┐    │
│   │ VN · EN · JA · ZH               │    │
│   │ (mobile: dời xuống dưới Lưu DB) │    │
│   └─────────────────────────────────┘    │
│                                          │
│   ┌─ Card (max-width 504px) ───────┐    │
│   │ TRI THỨC · PHÁP LUẬT · CÔNG NG │    │
│   │ (tagline-top, gold uppercase)   │    │
│   │                                 │    │
│   │      ╭──────────╮              │    │
│   │      │  Avatar  │ 180px tròn   │    │
│   │      ╰──────────╯              │    │
│   │                                 │    │
│   │   NGUYỄN TẤN PHONG (tên)       │    │
│   │   Chuyên gia Kinh tế số & PL   │    │
│   │   Luật gia - Trọng tài viên    │    │
│   │           ───                   │    │
│   │   Tư vấn chiến lược             │    │
│   │   TMĐT và Tự động hoá KD       │    │
│   │                                 │    │
│   │   [88px gap]                    │    │
│   │                                 │    │
│   │   QR-grid 5×2:                  │    │
│   │   ┌──────┬──┬──┬──┐            │    │
│   │   │  QR  │Z │F │📞│            │    │
│   │   │      ├──┼──┼──┤            │    │
│   │   │      │M │Y │L │            │    │
│   │   └──────┴──┴──┴──┘            │    │
│   │                                 │    │
│   │   ╔═══ LƯU DANH BẠ ═══╗        │    │
│   │   (gold gradient · vCard)       │    │
│   │                                 │    │
│   │   [Spacer 24px]                 │    │
│   │                                 │    │
│   │      ╭─ Chữ ký ─╮              │    │
│   │      │  140px    │              │    │
│   │      ╰───────────╯              │    │
│   │   © NGUYEN TAN PHONG.           │    │
│   │     ALL RIGHTS RESERVED.        │    │
│   └─────────────────────────────────┘    │
│ </body>                                  │
└─────────────────────────────────────────┘
```

---

## 📝 Content chi tiết

### Tagline (gold, uppercase, letter-spacing 0.35em)
> TRI THỨC · PHÁP LUẬT · CÔNG NGHỆ

### Tên + 4 dòng chức danh
- **NGUYỄN TẤN PHONG** (h1, gold, "Phong" bold)
- Chuyên gia Kinh tế số & Pháp luật
- Luật gia - Trọng tài viên
- (divider gold 40px)
- Tư vấn chiến lược
- Thương mại điện tử và Tự động hoá kinh doanh

### QR Grid (5×2 cells)
| Cell | Nội dung | Action |
|---|---|---|
| Lớn (2×2) | QR code (qr-tanphong.png) | scan → nguyentanphong.com |
| 1×1 | 💬 Zalo | zalo.me/0915159499 |
| 1×1 | f Facebook | facebook.com/tanphong1981 |
| 1×1 | 📞 Gọi | tel:+84915159499 |
| 1×1 | ✉ Email | mailto:hello@nguyentanphong.com |
| 1×1 | ▶ YouTube | youtube.com/@danmannong |
| 1×1 | in LinkedIn | linkedin.com/in/nguyentanphong |

### Nút "Lưu Danh Bạ"
- Gradient gold, full width 360px max
- Click → tải file `Nguyen-Tan-Phong.vcf` (vCard 3.0)
- vCard chứa: tên + chức danh + ORG (VECOM/CLEAD/TRACENT) + phone + email + URL + 3 social profiles

### Footer
- Chữ ký NguyenTanPhong.png (140px desktop · 120px mobile · filter brightness invert)
- © NGUYEN TAN PHONG. ALL RIGHTS RESERVED.

---

## 🎨 CSS Design Tokens

```css
--navy:       #1a1a1a   /* nền chính */
--cream:      #2C2C2C   /* nền card */
--gold:       #E0AA79   /* màu chính */
--gold-light: #f0c896   /* highlight */
--text:       #FFFFFF   /* text chính */
--text-soft:  rgba(255,255,255,0.5)
--border:     rgba(224,170,121,0.25)
```

### Pattern nền
- Zen circle SVG (data URI inline) repeat
- `stroke: #E0AA79` opacity 0.15

### Animations
- `fadeUp` 1.2s — text + avatar slide up khi load
- Stagger delays s2/s3/s4/s5 cho hiệu ứng tuần tự
- `vBlink` 2.2s — Zalo + Phone sidebar blink lệch phase 1.1s

---

## 💻 JavaScript Functions

### `saveContact()`
- Tạo vCard 3.0 string
- Blob + URL.createObjectURL → download
- GA event `save_contact`

### `trackEvent(name, params)`
- Wrapper cho gtag
- Nếu GA chưa load → silent fail

### `moveLangOnMobile()` (chỉ mobile ≤480px)
- Move `.lang-switcher` từ top-right vào dưới `.save-contact`
- Re-apply on window resize
- Desktop: position fixed top-right

---

## 🌐 SEO & Social

| Meta | Giá trị |
|---|---|
| Title | Nguyễn Tấn Phong \| TRI THỨC - PHÁP LUẬT - CÔNG NGHỆ |
| Description | Chuyên gia KTS & PL · Luật gia · Trọng tài viên · Tư vấn TMĐT và Tự động hoá kinh doanh |
| Canonical | `https://www.nguyentanphong.com/` |
| OG image | `/og-image.jpg` (1200×630) |
| Schema.org type | Person + ContactPoint |
| Robots | (không có noindex) — Google index full |

---

## 📂 Files liên quan

| File | Mục đích |
|---|---|
| `index.html` | = `coming-soon.html` content (production root) |
| `coming-soon.html` | Source of truth cho card simple |
| `avatar-nguyentanphong.jpg` | 49KB · ảnh đại diện |
| `NguyenTanPhong.png` | 16KB · chữ ký (filter invert white) |
| `qr-tanphong.png` | 70KB · QR code → nguyentanphong.com |
| `og-image.jpg` | 100KB · ảnh share FB/Zalo |
| `favicon-32.png` · `favicon.ico` · `apple-touch-icon.png` · `icon-192.png` | Icons PWA |
| `manifest.json` | PWA config |

---

## 🚀 Deployment

- **Host**: Vercel (Hobby plan free)
- **Domain**: nguyentanphong.com (apex) → www.nguyentanphong.com
- **Build**: Static · không có backend
- **CDN**: Vercel Edge Network (toàn cầu)
- **HTTPS**: Auto Let's Encrypt
- **Cache**: 
  - HTML: max-age=0, must-revalidate
  - Images (.png/.jpg/.webp): max-age=31536000 immutable

---

## 📊 Performance

| Chỉ số | Giá trị |
|---|---|
| Page size HTML | ~24KB |
| Total assets (avatar + chữ ký + QR + favicons) | ~140KB |
| Font Awesome CDN | ~100KB (cache cross-site) |
| Inter font | ~50KB |
| **First load total** | ~315KB (gzip ~120KB) |
| LCP (Largest Contentful Paint) | <1s |
| Lighthouse Performance | 95+ |

---

## 🔐 Security

- HTTPS forced + HSTS 2 năm
- CSP whitelist GA + FA + Fonts
- X-Frame-Options SAMEORIGIN
- X-Content-Type-Options nosniff
- Permissions-Policy block camera/mic/geo
- Font Awesome SRI integrity hash

---

## 📈 Analytics

- **GA4 ID**: `G-V45VVRDW8T` (tài khoản Nguyễn Tấn Phong)
- **Events tracked**:
  - `page_view` (auto)
  - `save_contact` — click nút Lưu Danh Bạ
  - `contact_zalo` / `contact_facebook` / `contact_call` / `contact_email` / `contact_youtube` / `contact_linkedin`
  - `lang_switch` (param: to=vi/en/ja/zh)

---

## 🔗 URL Routing

| URL | Hành vi |
|---|---|
| `/` | ✅ Trang Danh Thiếp (file này) |
| `/preview-full` · `/full` | 308 → `/` |
| `/en` · `/ja` · `/zh` | 308 → `/` |
| `/coming-soon` | 200 (duplicate, có noindex) |

---

## 📞 Contact info embed

```
Tên:      Nguyễn Tấn Phong
Phone:    +84 915 159 499
Email:    hello@nguyentanphong.com
Website:  https://www.nguyentanphong.com
Zalo:     https://zalo.me/0915159499
Facebook: https://facebook.com/tanphong1981
LinkedIn: https://www.linkedin.com/in/nguyentanphong
YouTube:  http://www.youtube.com/@danmannong
```

---

*File mô tả · cập nhật khi có thay đổi cấu trúc.*
