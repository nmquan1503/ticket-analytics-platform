# 📊 Ticket Analytics Platform

Hệ thống Quản trị và Phân tích Dữ liệu Vận hành Viễn thông, xây dựng đặc thù để hỗ trợ giám sát, truy vấn Sự Cố (SC) và Hỗ Trợ (HT).

Dự án bao gồm một Frontend hiển thị Dashboard chuẩn **Business Intelligence (BI)** và hệ thống giao diện **AI Copilot (Trợ lý Ảo)** để truy vấn SQL Data Warehouse.

---

## 📁 Cấu trúc thư mục nền tảng

```text
ticket-analytics-platform/
├── scc_ht_schema.sql     # Data Warehouse System Schema (Dimensional Modeling)
├── frontend/             # Ứng dụng BI Dashboard & AI Copilot
│   ├── src/
│   │   ├── components/   # Các Component Reusable
│   │   │   ├── AICopilot.jsx   # Cửa sổ Trợ lý ảo & SQL Workbench
│   │   │   ├── ChartCard.jsx   # Khung chứa Biểu đồ
│   │   │   ├── KPICard.jsx     # Thẻ đo lường chỉ số
│   │   │   └── MultiSelect.jsx # Bộ lọc Đa chiều Custom
│   │   ├── data/
│   │   │   └── mockData.js     # Factory Data để thao tác Frontend Real-Time
│   │   └── pages/
│   │       └── Dashboard.jsx   # Dashboard Layout Core (Lắp ghép)
│   ├── index.html        # Khung HTML gốc của Vite
│   ├── vite.config.js    # Cấu hình đóng gói Vite
│   ├── tailwind.config.js# Cấu hình hệ thống Design System 
│   ├── package.json      # Danh sách viện thuộc (React, Recharts, Lucide)
│   └── demo.html         # Phiên bản Web siêu tĩnh độc lập
└── README.md
```

---

## 🚀 Hướng dấn Cài đặt và Chạy ứng dụng CHI TIẾT

Ứng dụng Frontend được thiết kế bằng **React.js** kết hợp **Vite**. Do đó, yêu cầu cấu hình máy chủ phải có hệ điều hành cài đặt sẵn Node.js (phiên bản >16).

### BƯỚC 1: Khởi tạo và Tải thư viện
Mở Command Line (Terminal) và vào đúng thư mục frontend, sau đó tải Node Modules.
```bash
cd frontend
npm install
```

### BƯỚC 2: Khởi động Ứng dụng

Trong quá trình sử dụng thực tế, máy trạm nội bộ của bạn thường xuyên đầy bộ đệm (bị văng lỗi `ENOSPC` hệ thống theo dõi tệp). Vì vậy, có 2 cách để khởi động.

**Cách 1: Môi trường Phát triển (Development)** - Phù hợp nếu máy mạnh và bộ đệm chưa bị tràn.
```bash
npm run dev
```

**Cách 2: Môi trường Sản phẩm Tĩnh (Production Preview)** - **🌟 Rất khuyến nghị sử dụng🌟** (Khắc phục triệt để lỗi bộ đệm).
Hệ thống sẽ biên dịch code React thành mã nguồn độc lập tĩnh và phát trên máy chủ gọn nhẹ:
```bash
npm run build
npm run preview
```

**Kết nối URL:** 
Ứng dụng sẽ nổi lên tại cổng: [http://localhost:4173](http://localhost:4173) (nếu chạy Production) hoặc cổng 3000/5173 (nếu chạy Dev).

---

## 🔥 Các chức năng kỹ thuật Thượng tầng

### 1. AI Copilot & SQL Workbench
Ở góc dưới bên phải màn hình có một **Nút Kích Hoạt Tia Chớp nhấp nháy đỏ**. Khi bấm vào, **Sidebar AI** trượt ra.
- Nếu gõ câu thông thường: Hỏi số liệu.
- Nếu gõ câu bắt đầu bằng `SELECT` (SQL Query): Trả về lưới bảng dữ liệu bảng tĩnh siêu mượt như DataGrip.
- Sidebar phủ đè lên Dashboard (Overlay) giữ nguyên bối cảnh hiển thị số liệu giúp Sếp/Phân tích viên vừa nhìn bảng biểu vừa phân tích.

### 2. Analytics Đa chiều (Smart Routing Logic)
Bảng điểu khiển (Top Filter) sử dụng bộ lọc mảng đa thành phần (Array Multi Select) tự tay thiết kế chứ không dùng thư viện gốc:
- Lọc theo *Độ Ưu tiên (1 đến 6)*.
- Alert Nhấp Nháy rực lửa ngay bên dưới Filter khi lượng *Vé Khẩn Cấp (SOS)* tăng cao.

### 3. Phân Tích Gốc Rễ Đứt Cáp
Biểu đồ Recharts Rendering phân tích **Top 5 Nguồn cơn lỗi phần cứng** và **Tỷ lệ % đổ vỡ theo Nhóm Thiết bị IP**, tương thích ngược thiết kế với Schema Schema của MySQL Backend.

---
*Created and Optimized for Telecommunication Analytics Context.*
