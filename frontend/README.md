# 📊 Ticket Management BI Dashboard (Phase 2 - Full Integration)

Chào mừng bạn đến với hệ thống **Dashboard Phân tích Ticket Thông minh**, một nền tảng Business Intelligence (BI) cao cấp được thiết kế riêng để khai thác 100% dữ liệu từ hệ thống Sự Cố (SC) và Hỗ Trợ Kỹ Thuật (HT) dựa trên Schema SQL thực tế.

---

## 🛠 Công nghệ sử dụng (Tech Stack)

*   **Core:** React.js (Vite) - Tốc độ render và build siêu nhanh.
*   **Styling:** Tailwind CSS - Giao diện hiện đại, responsive, hỗ trợ Glassmorphism.
*   **Charts:** Recharts - Thư viện vẽ biểu đồ tương tác, mượt mà.
*   **Icons:** Lucide-React - Bộ icon vector chuyên nghiệp, tinh tế.
*   **Animation:** CSS Transitions & Keyframes - Hiệu ứng chuyển cảnh (fade-in, slide-up) mượt mà.

---

## 🏗 Kiến trúc Hệ thống (Architecture)

Dự án được thiết kế theo hướng **Component-Based Modular**, cho phép mở rộng quy mô dễ dàng:

### 1. Luồng dữ liệu (Data Pipeline)
*   `mockData.js`: Bộ engine sinh dữ liệu ảo thông minh, mô phỏng chính xác từng trường (field) trong SQL Schema:
    *   **SC Data:** Suspend time, Disaster flags, Auto vs Manual creation, Device types.
    *   **HT Data:** Escalated flags, Customer types, Service types, Rejection counts.

### 2. Giao diện Đa phân hệ (Multi-Tab Navigation)
Hệ thống không hiển thị dồn nén, mà phân tách thành 3 phân hệ phân tích sâu:

#### A. Tab Tổng quan (Overview Tab)
*   **KPIs Phủ rộng:** Tổng ticket, Tổng khách hàng ảnh hưởng, Tỷ lệ SLA, Thời gian xử lý trung bình.
*   **Status Distribution:** Biểu đồ tròn phân bổ trạng thái (New, In-progress, Resolved, Closed).
*   **Timeline Trend:** Biểu đồ Area theo dõi xu hướng phát sinh ticket theo ngày.
*   **Rankings:** Top 5 Chi nhánh bận rộn nhất & Top 5 Nhân sự xử lý tích cực nhất.
*   **Smart Mode (HT View):** Tự động kích hoạt biểu đồ **Tỷ lệ Leo thang (Escalation)** và **Phân loại Khách hàng** khi xem dữ liệu Hỗ trợ.

#### B. Tab Đánh giá Chất lượng (QoS/CX Tab)
*   **Độ trễ phản xạ (Creation Latency):** KPI đo thời gian trung bình từ khi lỗi phát sinh đến khi hệ thống báo về.
*   **Độ vênh thời gian (Time Gap):** Biểu đồ Bar xanh-đỏ so sánh Thời gian Thao tác (Actual) vs Thời gian Khách hàng bị chết mạng (Suspend).
*   **Auto-Pilot Tracking:** Theo dõi tỷ lệ hệ thống tự phát hiện lỗi (Auto Detection) vs khai báo thủ công.
*   **Anatomy of Risk:** Phân tích tính chất vi phạm (Chủ quan do con người vs Khách quan do thiên tai/hạ tầng).

#### C. Tab Phân tích Ùn tắc (Bottleneck Tab - Chế độ "Risk Focus")
*   **Bắt lỗi "Đá bóng trách nhiệm":** Theo dõi chỉ số `rejection_count` - số lần phòng ban từ chối nhận vé.
*   **Thời gian ngâm (Waiting Time):** Đo chỉ số `change_queue_time` - thời gian vé nằm chờ chuyển queue.
*   **Tuổi thọ tồn kho (Ticket Age):** Cảnh báo các vé "nợ xấu" nằm lâu trong hệ thống.
*   **Risk Chart (Dark Mode):** Biểu đồ ngang đặc biệt trên nền Slate-900 chuyên dùng để soi "Điểm đen" - Queue nào đang ngâm vé lâu nhất và đá bóng nhiều nhất.

### 3. Trợ lý AI SQL Copilot (Sidebar)
*   Tích hợp bên lề trái, cho phép người dùng trò chuyện để truy vấn dữ liệu.
*   Hỗ trợ hiển thị kết quả SQL dưới dạng bảng (Table) ngay trong khung Chat.

---

## 🧭 Hướng dẫn sử dụng & Vận hành

### 1. Cài đặt môi trường
Đảm bảo máy đã cài **Node.js**:
```bash
cd frontend
npm install
```

### 2. Chế độ Phát triển (Development)
Sử dụng để chỉnh sửa code và xem thay đổi ngay lập tức:
```bash
npm run dev
```

### 3. Đóng gói Sản xuất (Production Build)
Lệnh này sẽ tối ưu hóa mã nguồn, nén dung lượng để triển khai lên Server:
```bash
npm run build
```
*Kết quả sẽ nằm trong thư mục `dist/`.*

### 4. Xem kết quả Build
Sử dụng sau khi build xong để kiểm tra bản production local:
```bash
npm run preview
```

---

## 🌟 Tính năng "Đắt giá" trong Code
*   **Multi-Select Filters:** Bộ lọc Chi nhánh, Vùng miền, Mức độ ưu tiên hỗ trợ chọn nhiều mục cùng lúc.
*   **Hierarchical Cascading Filter:** Logic lọc phân cấp thông minh (Khu vực ➡️ Chi nhánh) giúp dữ liệu luôn nhất quán.
*   **Real-time Filter Logic:** Dữ liệu tự động tính toán lại tức thì qua `useMemo` khi người dùng thay đổi bất kỳ bộ lọc nào.
*   **Responsive Design:** Tự động co giãn từ màn hình Laptop 2K đến màn hình điện thoại di động (Mobile).
*   **Icon-Sync:** Hệ thống icon Lucide đồng bộ hoàn toàn với phiên bản thư viện v0.284.0 để đảm bảo không bị crash UI.

---

## 🧪 Hướng dẫn Kiểm thử Giao diện (GUI Testing Guide)

Để đảm bảo Dashboard vận hành đúng kịch bản, sếp có thể thực hiện các bước kiểm thử sau:

### 1. Kiểm tra Chế độ hiển thị (Mode Switching)
*   **Kịch bản:** Bấm nút chuyển đổi giữa **Sự Cố (SC)** và **Hỗ Trợ (HT)** ở phía trên cùng bên trái.
*   **Yêu cầu:** Các con số KPI phải nhảy lại tức thì. Tab Tổng quan phải hiển thị thêm Biểu đồ Leo thang khi ở chế độ HT.

### 2. Kiểm tra Luồng Tab (Tab Navigation)
*   Bấm lần lượt qua 3 Tab: **Tổng quan**, **Chất lượng**, **Ùn tắc**.
*   **Yêu cầu:** Hiệu ứng Fade-in phải mượt mà, các biểu đồ không bị tràn khung hoặc biến mất.

### 3. Kiểm tra Bộ lọc (Filtering Logic)
*   Thử chọn nhiều Chi nhánh hoặc Khu vực cùng lúc trong menu thả xuống.
*   **Yêu cầu:** Dữ liệu biểu đồ phải co giãn tương ứng với danh sách mục đã chọn. Bấm nút **"Xóa bộ lọc"** để đưa mọi thứ về mặc định.

### 4. Kiểm tra Biểu đồ Tương tác (Chart Interactivity)
*   Di chuột vào các cột hoặc đường trong biểu đồ.
*   **Yêu cầu:** Phải hiện **Tooltip** hiển thị chi tiết con số dưới dạng Pop-up tại điểm di chuột.

### 5. Kiểm tra Trợ lý AI (AI Copilot Sidebar)
*   Bấm vào biểu tượng Chat ở cạnh trái màn hình.
*   **Yêu cầu:** Thanh Sidebar phải trượt ra từ bên trái. Gõ thử nội dung để kiểm tra giao diện khung chat.

### 6. Kiểm tra Độ tương thích (Responsiveness)
*   Nhấn `F12` trên trình duyệt, chọn chế độ Mobile hoặc co bóp cửa sổ trình duyệt.
*   **Yêu cầu:** Grid 5 cột của bộ lọc phải tự động chuyển thành 1 cột (dọc) trên điện thoại và biểu đồ tự động co nhỏ lại.

---

## 🧠 Cơ chế Giao diện Thông minh (Smart UI Logic)

Hệ thống được tích hợp các logic xử lý giao diện tự động để tối ưu trải nghiệm người dùng, tránh gây tràn ngập thông tin:

### 1. Phân cấp Chế độ xem (View Mode Context)
Dashboard có hai "linh hồn" dữ liệu khác nhau là **Sự Cố (SC)** và **Hỗ Trợ (HT)**. 
*   **Chế độ Mặc định (SC):** Giao diện sẽ tập trung vào hạ tầng, thiết bị và các chỉ số kỹ thuật thuần túy.
*   **Chế độ Nâng cao (HT):** Khi sếp bấm nút **Hỗ Trợ (HT)**, hệ thống sẽ tự động "mở khoá" và kích hoạt thêm các biểu đồ chuyên biệt ở dưới cùng như:
    *   **Tỷ lệ Vượt tuyến (Escalation Rate):** Đo lường tính tự chủ của các chi nhánh.
    *   **Phân khúc Khách hàng:** Phân tích trọng tâm khách hàng doanh nghiệp, tập đoàn...
*   *Lợi ích:* Giúp Dashboard luôn gọn gàng nhưng vẫn đầy đủ chiều sâu khi cần thiết.

### 2. Logic Bộ lọc Phân cấp (Cascading Filters)
Thay vì để sếp phải tìm kiếm trong danh sách hàng trăm chi nhánh, hệ thống sử dụng logic lọc cha-con:
*   **Khu vực (Cha):** Khi sếp chọn "Hà Nội", "Đà Nẵng", v.v.
*   **Chi nhánh (Con):** Danh sách chi nhánh sẽ tự động lọc lại, chỉ hiển thị những chi nhánh thuộc vùng địa lý đó.
*   **Xác thực dữ liệu:** Nếu sếp đổi khu vực khác, các chi nhánh cũ đã chọn sẽ tự động được dọn dẹp để tránh sai sót dữ liệu.

### 3. Hệ thống Cảnh báo Thông minh (Alert Banner)
Dashboard không chỉ là những biểu đồ vô tri. Hệ thống sẽ quét toàn bộ dữ liệu theo thời gian thực:
*   Nếu phát hiện Ticket có cờ **SOS** hoặc Ticket **Mức ưu tiên 5-6** (Cực kỳ khẩn cấp), một **Banner đỏ cảnh báo** sẽ tự động hiện lên với hiệu ứng nhấp nháy để nhắc sếp xử lý ngay.

### 4. Tương tác BI 360 độ
*   **Tooltip:** Di chuột vào bất kỳ điểm nào trên biểu đồ để xem con số chi tiết đến từng đơn vị.
*   **Responsive:** Grid lọc 5 cột tự động co giãn cực kỳ linh hoạt, đảm bảo sếp dùng máy tính bảng hay điện thoại vẫn thao tác chuẩn xác.

---

**✍️ Được phát triển bởi:** Antigravity AI Partner


**📅 Phiên bản:** 2.0.0 (Full SQL Schema Integration)
