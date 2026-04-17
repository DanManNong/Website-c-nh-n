# 🚀 DEPLOY GUIDE — Website Nguyễn Tấn Phong

> Hướng dẫn thiết lập workflow `dev` / `main` + Vercel cho repo `DanManNong/Website-c-nh-n`.

---

## 🧭 Kiến trúc deploy

```
Local folder (NguyenTanPhong/)
       │
       ├── git push main  →  Vercel Production  →  nguyentanphong.com   (banner ẨN)
       └── git push dev   →  Vercel Preview     →  *.vercel.app          (banner HIỆN)
```

Banner staging đỏ tự động hiện trên mọi URL **không phải** `nguyentanphong.com` hoặc `www.nguyentanphong.com` — nhờ đoạn JS check `location.hostname` trong mỗi HTML file.

---

## ⚙️ Lần đầu setup — chú chạy trên Terminal 1 lần

```bash
# 1. Vào thư mục repo (chú thay path đúng nơi có git)
cd "/đường/dẫn/đến/Website-c-nh-n"

# 2. Đảm bảo đã cấu hình git identity (nếu chưa)
git config user.name "Nguyễn Tấn Phong"
git config user.email "hello@nguyentanphong.com"

# 3. Lấy code mới nhất từ main
git checkout main
git pull origin main

# 4. Tạo branch dev + push lên remote
git checkout -b dev
git push -u origin dev
```

→ Sau bước này repo có 2 branch: `main` (production) + `dev` (staging).

---

## 🔴 Workflow hằng ngày — `SỬA CHỮA`

Khi chú nhắn **`SỬA CHỮA`**, cháu sẽ làm:

```bash
# (cháu) đang ở branch dev
git checkout dev
# ... chỉnh code theo yêu cầu ...
git add .
git commit -m "fix: Z04 — sửa số đối tác"
git tag -a v6.0.1 -m "Snapshot sau khi sửa Z04"
git push origin dev
git push --tags
```

→ Vercel tự build preview URL (ví dụ `website-c-nh-n-git-dev-danmannong.vercel.app`).
→ Banner đỏ **hiện** vì hostname khác `nguyentanphong.com`.
→ Chú vào URL preview kiểm tra, khi ok thì nhắn `LIVE`.

---

## 🟢 Khi chú nhắn `LIVE` — đẩy lên production

```bash
git checkout main
git merge dev --ff-only      # fast-forward only, không tạo merge commit
git push origin main
git checkout dev              # quay lại dev để tiếp tục sửa
```

→ Vercel tự deploy lên `nguyentanphong.com`.
→ Banner **ẩn** vì đúng hostname production.

---

## 🏷 Quy tắc version (semver)

| Loại sửa | Bump | Ví dụ |
|---|---|---|
| Tweak nhỏ (text, màu, dời 1 chỗ) | **patch** | v6.0.0 → v6.0.1 |
| Thêm tính năng / sửa vừa | **minor** | v6.0.0 → v6.1.0 |
| Rework lớn / đổi cấu trúc | **major** | v6.0.0 → v7.0.0 |

Tag luôn đẩy lên remote: `git push --tags`.

---

## ↩️ Rollback nếu lỡ tay

```bash
# Xem danh sách tag
git tag --sort=-v:refname | head -10

# Reset main về tag an toàn
git checkout main
git reset --hard v6.0.0
git push --force origin main
```

⚠️ Chỉ force push khi thực sự cần — cháu sẽ hỏi xác nhận trước.

---

## 🏠 Preview local khi đang sửa

```bash
cd "/Users/nguyentanphong/Desktop/WEB - CÁC ĐƠN VỊ/NguyenTanPhong"
python3 -m http.server 8000
open http://localhost:8000/
```

→ Banner tự hiện vì hostname = `localhost`.

---

## ✅ Checklist trước khi chú nhắn `LIVE`

- [ ] Preview URL (`*.vercel.app`) vào xem ok
- [ ] Mobile + desktop đều kiểm tra (test ở Chrome DevTools)
- [ ] Các link nội bộ còn sống (v3, ve_toi, tai_lieu, article_detail, thuong_hieu)
- [ ] Modals (QR, Password, Register) đóng/mở không lỗi
- [ ] SĐT + email + Zalo + Facebook links đúng
- [ ] Ảnh avatar + chữ ký load được
- [ ] Banner staging đỏ HIỆN ở preview, SẼ ẨN trên production

---

## 📂 File cấu hình trong repo

| File | Mục đích |
|---|---|
| `vercel.json` | Clean URLs · headers bảo mật · cache ảnh |
| `.vercelignore` | Loại MD / Excel / script nội bộ khỏi deploy |
| `.gitignore` | Loại `.DS_Store` · `.claude/` · credentials |
| `ZONE-MAP.md` | Bản đồ vùng Z01-Z15 + modals + trang phụ |
| `QUY-UOC-LAM-VIEC.md` | Protocol làm việc cháu ↔ chú |

---

## 🔗 Links nhanh

- **Repo:** https://github.com/DanManNong/Website-c-nh-n
- **Vercel preview:** `website-c-nh-n.vercel.app`
- **Production:** `nguyentanphong.com`

---

*File cập nhật: 2026-04-17.*
