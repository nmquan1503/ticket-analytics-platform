# 📘 Hướng dẫn Chiến lược Tích hợp Backend cho Dashboard

Tài liệu này hướng dẫn chi tiết cách chuyển đổi Dashboard từ dữ liệu giả lập (Mock Data) sang dữ liệu thực tế từ Database thông qua một lớp API Backend.

---

## 1. Các thành phần cần chuẩn bị
Để hệ thống hoạt động, sếp cần có:
1.  **Cơ sở dữ liệu:** Oracle 23ai hoặc SQL Server (theo file `.sql` sếp đã cung cấp).
2.  **API Server:** Một máy chủ (Node.js, Python, hoặc Java) để thực hiện các câu lệnh SQL.
3.  **Endpoint:** Một địa chỉ web (ví dụ: `http://localhost:8080/api/tickets`) trả về dữ liệu JSON.

---

## 2. Các bước thay đổi mã nguồn Frontend

### Bước 1: Cài đặt công cụ kết nối
Chạy lệnh sau trong thư mục `frontend`:
```bash
npm install axios
```

### Bước 2: Khai báo URL Backend
Tạo file `.env` trong thư mục `frontend`:
```env
VITE_API_BASE_URL=http://localhost:8080/api
```

### Bước 3: Thay đổi logic tại `src/pages/Dashboard.jsx`

Tìm đoạn code đang sử dụng `mockSCData` hoặc `mockHTData` và thay thế bằng logic sau:

```javascript
import axios from 'axios';
import { useState, useEffect } from 'react';

// ... trong function Dashboard()
const [data, setData] = useState([]);
const [isLoading, setIsLoading] = useState(true);

useEffect(() => {
    const fetchData = async () => {
        setIsLoading(true);
        try {
            // viewMode là 'SC' hoặc 'HT'
            const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/tickets`, {
                params: { 
                    type: viewMode,
                    date_range: dateRange 
                }
            });
            setData(response.data);
        } catch (error) {
            console.error("Lỗi khi lấy dữ liệu từ Backend:", error);
        } finally {
            setIsLoading(false);
        }
    };
    fetchData();
}, [viewMode, dateRange]); // Gọi lại API khi sếp đổi Tab hoặc đổi Thời gian
```

---

## 3. Cấu trúc dữ liệu JSON Backend cần trả về
Backend của sếp phải trả về một mảng các đối tượng (Array of Objects) với tên thuộc tính **Y HỆT** như sau để biểu đồ không bị lỗi:

| Thuộc tính | Kiểu dữ liệu | Ý nghĩa |
| :--- | :--- | :--- |
| `ticket_id` | Number | ID định danh |
| `status` | String | 'New', 'Inprogress', 'Resolved', 'Closed' |
| `location` | String | Tên khu vực (ví dụ: '01. Hà Nội') |
| `branch_name` | String | Tên chi nhánh (ví dụ: 'Hà Nội 1') |
| `actual_time` | Number | Thời gian thao tác (phút) |
| `suspend_time` | Number | Thời gian gián đoạn (phút) |
| `rejection_count` | Number | Số lần từ chối nhận vé |
| `sla_status` | String | 'Đúng hạn' hoặc 'Quá hạn' |

---

## 4. Giải quyết các vấn đề thường gặp

### A. Lỗi CORS (Cross-Origin Resource Sharing)
Đây là lỗi phổ biến nhất. Sếp cần cấu hình Backend cho phép domain của Dashboard truy cập.
- **Node.js:** `app.use(require('cors')())`
- **Python FastAPI:** Sử dụng `CORSMiddleware`.

### B. Hiển thị trạng thái đang tải (Loading)
Trong file `Dashboard.jsx`, sếp hãy thêm đoạn code này trước phần `return`:
```javascript
if (isLoading) {
    return (
        <div className="flex items-center justify-center h-screen bg-slate-50">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            <p className="ml-3 font-bold text-gray-500">Đang đồng bộ dữ liệu từ Database...</p>
        </div>
    );
}
```

### C. Bảo mật API
- Luôn sử dụng `HTTPS` khi triển khai thực tế.
- Thêm một lớp Token (ví dụ: Bearer Token) để chỉ Dashboard của sếp mới có quyền lấy dữ liệu.

---

**Chúc sếp triển khai Backend thành công! Dashboard này đã được thiết kế cực kỳ linh hoạt để sếp "cắm dây" phát ăn ngay.**
