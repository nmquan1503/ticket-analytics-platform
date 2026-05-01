from app.services.chat.workflow.graph_state import GraphState
from app.db.oracle_client import db_client
from datetime import date
from app.services.chat.bot import get_sql_res

def validate_sql(state: GraphState):
    num_retries = 3
    for i in range(num_retries):
        try:
            rows = db_client.fetch_all(state["sql_query"])
            state["validated"] = True
            state["results"] = rows
            return state
        except Exception as e:
            print(e)
            db_description = state["db_description"]
    
            current_date = date.today()
            
            schema_info = ""
            for table in state["schema"]:
                table_name = table["table_name"]
                table_comment = table["table_comment"]
                schema_info += f"(Table){table_name} - {table_comment}:\n"
                for column in table["columns"]:
                    column_name = column["column_name"]
                    column_comment = column["column_comment"]
                    schema_info += f"\t(Column){column_name} - {column_comment}\n"
            
            kws_str = ""
            for k, v in state["keywords"].items():
                kws_str += f"{k}: {v}\n"
            
            values_str = ""
            for table in state["schema"]:
                table_name = table["table_name"]
                values_str += f"(Table){table_name}:\n"
                for column in table["columns"]:
                    values = column["values"]
                    values_str += f"\t(Column){column_name}: {str(values)}\n"
            
            prompt = f"""
Bạn là một trợ lý SQL chuyên nghiệp. Nhiệm vụ của bạn là **sửa truy vấn Oracle SQL hiện tại** để nó **đúng, đầy đủ và chính xác với câu hỏi của người dùng**, không thừa, không thiếu.


Đầu vào gồm:
- **Mô tả schema**: thông tin các bảng và cột liên quan đến câu hỏi, mỗi bảng có mô tả chi tiết; mỗi cột có chú thích về ý nghĩa, lưu ý hoặc điểm đặc biệt.
- **Distinct values**: các giá trị đặc trưng của các trường quan trọng, dùng để suy luận ngữ nghĩa các entity trong câu hỏi.
- **Keywords**: từ khóa, viết tắt thường dùng trong hệ thống.
- **Câu hỏi hiện tại của người dùng**
- **Truy vấn SQL hiện tại**
- **Thông tin lỗi khi chạy truy vấn**

Yêu cầu khi sửa truy vấn:
- Dựa trên câu hỏi, schema, distinct values, keywords và lỗi để xác định **đúng, đầy đủ các bảng, cột và điều kiện**.
- Sửa các lỗi trong truy vấn hiện tại: sai bảng, sai cột, thiếu JOIN, sai điều kiện, sai logic.
- Ưu tiên giữ cấu trúc truy vấn hiện tại, chỉ chỉnh sửa phần cần thiết; nếu truy vấn sai hoàn toàn thì viết lại.
- Suy luận ngữ nghĩa các entity trong câu hỏi dựa vào distinct values và mô tả schema (không phân biệt chữ hoa, chữ thường).
- Chọn phép so sánh phù hợp:
   + Entity là giá trị xác định, duy nhất → dùng `=`.
   + Entity là đoạn văn, mô tả hoặc text dài → cân nhắc dùng `LIKE`.
- Phân tích kỹ các bảng, cột, đặc biệt cột liên quan điều kiện; xem xét cả cột cần để lọc nhưng không nhắc trực tiếp trong câu hỏi.
- Phân biệt rõ mục tiêu và điều kiện; không thêm bừa bảng, cột, JOIN hay điều kiện.
- JOIN chỉ khi cần dữ liệu từ nhiều bảng; WHERE chỉ chứa điều kiện từ câu hỏi hoặc cần để join.
- Truy vấn phải dựa hoàn toàn trên thông tin cung cấp.
- Có thể bổ sung điều kiện về thời gian dựa vào ngày hiện tại nếu cần.
- Phân tích ý định câu hỏi để chọn đúng phép toán như COUNT, SUM,...
- Đảm bảo chỉ sử dụng đúng hệ thống liên quan trong câu hỏi.
- Nếu thông tin không đủ rõ ràng để xác định chính xác, hãy trả về câu hỏi làm rõ thay vì SQL.
- Sau khi sửa xong, **chỉ trả về truy vấn SQL**, không giải thích.

Thông tin đầu vào:
- **Mô tả hệ thống**:
{db_description}

- **Ngày hiện tại**:
{current_date}

- **Schema**:
{schema_info}

- **Keywords**:
{kws_str}

- **Distinct values**:
{values_str}

- **Câu hỏi hiện tại**:
{state["question"]}

- **Truy vấn SQL hiện tại**:
{state["sql_query"]}

- **Lỗi khi chạy**:
{str(e)}
"""
            sql = get_sql_res(prompt)
            print(sql)
            print('=' * 10)
            state["sql_query"] = sql
    

    state["validated"] = False
    state['answer'] = f"Không thể tạo truy vấn SQL hợp lệ. Vui lòng thử lại với câu hỏi cụ thể hơn."
    state["results"] = []
    return state

if __name__ == "__main__":
    # ========== Chuẩn bị state giả lập ==========
    # Tái sử dụng schema từ test gen_sql trước đó
    test_state = {
        "db_description": (
            "Hệ thống quản lý ticket tích hợp, quản lý đồng thời cả ticket sự cố (SC) "
            "và ticket hỗ trợ kỹ thuật (HT). Hệ thống SC hỗ trợ truy vấn sự cố kỹ thuật phát sinh "
            "trên hạ tầng, bao gồm thời gian, thiết bị, POP, nguyên nhân, ảnh hưởng khách hàng "
            "và hiệu quả xử lý. Hệ thống HT hỗ trợ truy vấn ticket hỗ trợ kỹ thuật theo tiến trình "
            "xử lý, SLA, queue/đơn vị xử lý, nhân sự và lịch sử cập nhật."
        ),
        "question": "Số lượng ticket SC hôm qua",
        "schema": [
            {
                "table_name": "FACT_SC_TICKETS",
                "table_comment": "Bảng ticket sự cố",
                "columns": [
                    {"column_name": "TICKET_ID", "column_comment": "ID ticket", "values": []},
                    {"column_name": "SC_KHG_STATUS", "column_comment": "Trạng thái ảnh hưởng khách hàng (Có/Không)", "values": ["Có", "Không"]}
                ]
            },
            {
                "table_name": "FACT_TICKETS",
                "table_comment": "Bảng ticket chung",
                "columns": [
                    {"column_name": "CREATION_ID", "column_comment": "ID khởi tạo", "values": []}
                ]
            },
            {
                "table_name": "FACT_TICKET_CREATION",
                "table_comment": "Bảng thông tin khởi tạo",
                "columns": [
                    {"column_name": "date", "column_comment": "Ngày khởi tạo", "values": []},
                    {"column_name": "shift", "column_comment": "Ca trực", "values": ["Ca 1", "Ca 2"]}
                ]
            }
        ],
        "keywords": {
            "hôm qua": "TRUNC(SYSDATE)-1",
            "nay": "TRUNC(SYSDATE)"
        },
        "examples": [],  # không cần cho validate
        # ===== SQL sai =====
        "sql_query": (
            "SELECT COUNT(*)\n"
            "FROM fact_sc_tickets s\n"
            "JOIN fact_tickets t ON s.ticket_id = t.id\n"
            "JOIN fact_ticket_creation c ON t.creation_id = c.id\n"
            "WHERE c.date = TRUNC(SYSDATE)-1"  # <= LỖI: cột date cần dấu ngoặc kép nếu dùng chữ thường
        ),
        "validated": False,
        "results": []
    }

    print("Bắt đầu test validate_sql...\n")
    print("SQL ban đầu (sai):\n", test_state["sql_query"])

    # Gọi hàm validate_sql
    updated_state = validate_sql(test_state)

    print("\nKết quả:")
    print("- Validated:", updated_state.get("validated"))
    print("- SQL sau sửa:")
    print(updated_state.get("sql_query"))
    if updated_state.get("validated"):
        print("- Kết quả truy vấn (3 dòng đầu):")
        for row in updated_state.get("results", [])[:3]:
            print(row)
    else:
        print("- Thông báo lỗi:", updated_state.get("answer"))