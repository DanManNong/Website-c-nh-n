# Pháp lý Network Hướng Dương

Visualize cấu trúc văn bản pháp luật Việt Nam dạng bản đồ tương tác.

## Deploy lên GitHub Pages

1. Tạo repo mới tên `phaply-network` (public)
2. Upload toàn bộ thư mục này
3. Settings → Pages → Source: **main branch / root**
4. URL: `https://[username].github.io/phaply-network/`

## Nhúng vào Squarespace

Trong trang muốn nhúng, thêm **Code Block**:
```html
<iframe 
  src="https://[username].github.io/phaply-network/viewer.html?laws=luat_122_2025"
  width="100%" 
  height="85vh" 
  frameborder="0"
  style="border-radius:12px">
</iframe>
```

## Thêm luật mới

1. Tạo file `data/luat_xxx_yyyy.js` theo format `luat_122_2025.js`
2. Thêm entry vào `data/manifest.json`
3. Xuất hiện tự động trong `index.html`

## So sánh 2 luật song song

`viewer.html?laws=luat_122_2025,luat_116_2025`
