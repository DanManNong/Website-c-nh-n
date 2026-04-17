# 🗺 ZONE MAP — Website Nguyễn Tấn Phong

> Quy ước đặt tên vùng để trao đổi nhanh. Chú nhắn "sửa Z04", "đổi màu Z07" → cháu vào code đúng chỗ.
> Cập nhật: 2026-04-17

---

## 🏠 Trang chủ — `wireframe_nguyentanphong_v3.html`

| Mã | Vùng | Dòng (ước lượng) | Nội dung |
|---|---|---|---|
| **Z01** | Language Bar | 753 | Thanh chọn ngôn ngữ VN · EN · CN · KR · JP |
| **Z02** | Nav | 762 | Logo "Nguyễn Tấn Phong" + menu + nút Danh Thiếp |
| **Z03** | Hero | 776 | Avatar tròn + tên + sub-title + tagline + CTA |
| **Z04** | Stats | 793 | 4 chỉ số: 10+ năm · 05 vai trò · 100+ bài · 6,875 đối tác |
| **Z05** | Vai Trò Chuyên Môn | 816 | 5 tổ chức: VECOM · CLEAD · ARI · TRACENT · Eagle |
| **Z06** | Góc Nhìn & Tri Thức | 852 | 3 bài viết nổi bật (link NLD / VnExpress) |
| **Z07** | Báo Chí Đưa Tin | 892 | 7 đầu báo: NLD · VnExpress · Tuổi Trẻ · Thanh Niên · Tiền Phong · PLO · Công Thương |
| **Z08** | Thư Viện Tri Thức | 911 | 8 chuyên đề bài giảng (A-D active, E-H locked) |
| **Z09** | Document Section | 943 | Counter `00006875` + mô tả tài liệu |
| **Z10** | Manifesto Preview | 960 | Đoạn preview "Về Tôi" → link sang `wireframe_ve_toi.html` |
| **Z11** | Chuyên Mục | 972 | 5 lĩnh vực: Kinh tế số · BĐS · An ninh mạng · Trọng tài · Pháp luật |
| **Z12** | Lead Magnet | 989 | Cẩm nang Pháp lý & Kinh tế số 2026 |
| **Z13** | Contact Grid | 1015 | 6 kênh liên hệ (Phone · Email · Zalo · Facebook · LinkedIn · YouTube) |
| **Z14** | Footer | 1033 | Chữ ký NguyenTanPhong.png + links + copyright |
| **Z15** | Scroll-to-top | 1051 | Nút tròn float góc phải |

---

## 🪟 Modals (dùng cho mọi trang)

| Mã | Modal | Nội dung |
|---|---|---|
| **M-QR** | QR Card | Danh thiếp điện tử — QR + thông tin liên hệ |
| **M-PASS** | Password Gate | Cổng mật khẩu vào thư viện (Z08) |
| **M-REG** | Register | Form đăng ký nhận tài liệu / lead magnet (Z12) |

---

## 📄 Trang phụ

| Mã | File | Nội dung |
|---|---|---|
| **P-VeToi** | `wireframe_ve_toi.html` | Trang giới thiệu cá nhân — 5 vai trò, digital card |
| **P-TaiLieu** | `wireframe_tai_lieu.html` | Thư viện tài liệu — filter theo chuyên mục |
| **P-Article** | `wireframe_article_detail.html` | Trang chi tiết 1 bài viết |
| **P-ThuongHieu** | `thuong_hieu_so_phong.html` | Thương hiệu cá nhân — bio 1/150/300 từ |
| **E404** | `404.html` | Trang lỗi 404 brand-consistent |
| **E-Coming** | `coming-soon.html` | Trang tạm — avatar + QR + SĐT |
| **ENTRY** | `index.html` | Redirect → v3 (Vercel entry point) |

---

## 🎨 Brand tokens (CSS variables)

| Token | Value | Dùng cho |
|---|---|---|
| `--navy` | `#1a1a1a` | Chữ tối / nền đen |
| `--cream` | `#2C2C2C` | Nền chính dark mode |
| `--gold` | `#E0AA79` | Accent chính |
| `--gold-light` | `#f0c896` | Accent hover |
| `--text` | `#FFFFFF` | Chữ chính |
| `--text-soft` | `rgba(255,255,255,0.5)` | Chữ phụ |
| `--border` | `rgba(224,170,121,0.25)` | Viền box |

---

## 🛠 Quy ước sửa

- Chú nhắn `Z04` → cháu mở v3, tới vùng Stats
- Chú nhắn `M-QR` → cháu mở modal danh thiếp
- Chú nhắn `P-VeToi Z03` → cháu mở trang Về Tôi, vùng 3
- Chú nhắn `footer tất cả` → cháu sửa `Z14` + footer của mọi trang phụ

---

*File này cập nhật khi thêm vùng mới hoặc đổi cấu trúc.*
