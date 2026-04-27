# 📊 Ticket Analytics Platform

Nền tảng Quản trị và Phân tích Dữ liệu Vận hành Viễn thông, tập trung vào việc bóc tách số liệu cho các luồng Sự Cố (SC) và Hỗ Trợ (HT).

Dự án bao gồm một Frontend hiển thị Dashboard chuẩn Business Intelligence (BI) và một hệ thống mô phỏng cơ sở dữ liệu Data Warehouse.

---

## 📁 Cấu trúc thư mục

```text
ticket-analytics-platform/
├── scc_ht_schema.sql     # File cấu trúc CSDL SQL (Data Warehouse)
├── frontend/             # Ứng dụng lõi BI Dashboard (React + Vite + Tailwind)
│   ├── src/
│   │   ├── components/   # Các UI Components (KPICard, ChartCard, MultiSelect)
│   │   ├── data/         # Hệ thống giả lập Mock Data phản ánh schema SQL
│   │   └── pages/        # Dashboard Layout
│   └── demo.html         # File chạy Demo tĩnh trực tiếp (Không cần Node.js)
└── README.md
```

---

## 🚀 Hướng dẫn cài đặt và sử dụng

### Dành cho người không chuyên (Chạy xem Demo ngẫu nhiên)
Bạn có thể mở trực tiếp file `frontend/demo.html` bằng bất kỳ trình duyệt web nào (Chrome, Edge, Firefox) để xem giao diện tĩnh. Giao diện tĩnh này có tích hợp sẵn code JavaScript giả lập.

### Dành cho Developer (Chạy App React thực tế)
Yêu cầu hệ thống phải được cài đặt `Node.js` (Phiên bản > 16.x).

**Bước 1:** Di chuyển vào thư mục chứa code giao diện.
```bash
cd frontend
```

**Bước 2:** Cài đặt các thư viện cần thiết.
```bash
npm install
```

**Bước 3:** Khởi động dự án trên trình duyệt.

🔹 *Cách 1: Chạy môi trường Phát triển (Nhẹ nhàng, theo dõi code trực tiếp)*
```bash
npm run dev
```

🔹 *Cách 2: Chạy môi trường Giả lập Production (Khuyên dùng khi máy tính gặp lỗi quá tải system watchers / ENOSPC Error)*
```bash
npm run build
npm run preview
```

Ứng dụng sẽ tự động chạy tại cổng: `http://localhost:4173` hoặc `http://localhost:3000`.

---

## 🔥 Tính năng Nổi bật trong Dashboard

1. **Global Multiple-Select Filter**: Cho phép người xem lọc đồng thời cực kỳ linh hoạt (Nhiều Khung thời gian, Nhiều Khu vực và Nhiều Chi nhánh cùng một lúc).
2. **Alert Điểm Nóng (SOS Box)**: Hệ thống tự động đẩy cảnh báo rung (pulse) dạng biểu ngữ lên trên top khi có các Ticket thuộc mức **Ưu tiên từ 5-6** hoặc **được đánh cờ khẩn cấp (SOS).**
3. **Phân tích Gốc rễ (Root Causes)**: Biểu đồ theo dõi Lỗ hổng thường gặp nhất trong hệ thống và Phân bổ Nhóm thiết bị (Access, Core IP, Transmission) tạo ra chúng.
4. **Ranking Nhân sự / Chi nhánh**: Xếp hạng khách quan năng lực xử lý ticket.

---
*Developed & Optimized by Antigravity AI.*
