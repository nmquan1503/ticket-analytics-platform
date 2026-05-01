from app.services.chat.workflow.graph_state import GraphState
from datetime import date
from app.services.chat.bot import get_sql_res

def gen_sql(state: GraphState):
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
    
    ex_str = ""
    for item in state["examples"]:
        ex_str += f"""
    - Câu hỏi ví dụ: {item["question"]}
        **Đáp án SQL ví dụ**: {item["answer"]}

"""
    
    prompt = f"""
Bạn là một trợ lý SQL chuyên nghiệp. Nhiệm vụ của bạn là **tạo truy vấn Oracle chính xác** cho câu hỏi của người dùng, đảm bảo đầy đủ và chính xác các bảng, cột và điều kiện, không thừa, không thiếu.


Đầu vào gồm:
- **Mô tả schema**: thông tin các bảng và cột liên quan đến câu hỏi, mỗi bảng có mô tả chi tiết; mỗi cột có chú thích về ý nghĩa, lưu ý hoặc điểm đặc biệt.
- **Distinct values**: các giá trị đặc trưng của các trường quan trọng, dùng để suy luận ngữ nghĩa các entity trong câu hỏi.
- **Keywords**: từ khóa, viết tắt thường dùng trong hệ thống.
- **Câu hỏi hiện tại của người dùng**

Yêu cầu khi tạo truy vấn:
- Dựa trên câu hỏi, schema, distinct values và keywords để xác định **đúng, đầy đủ các bảng, cột và điều kiện**.
- Suy luận ngữ nghĩa các entity trong câu hỏi dựa vào distinct values và mô tả schema (không phân biệt chữ hoa, chữ thường).
- Chọn phép so sánh phù hợp:
   + Entity là giá trị xác định, duy nhất → dùng `=`.
   + Entity là đoạn văn, mô tả hoặc text dài → cân nhắc dùng `LIKE`.
- Phân tích kỹ các bảng, cột, đặc biệt cột liên quan điều kiện; xem xét cả cột cần để lọc nhưng không nhắc trực tiếp trong câu hỏi.
- Phân biệt rõ mục tiêu và điều kiện; không thêm bừa bảng, cột, JOIN hay điều kiện.
- JOIN chỉ khi cần dữ liệu từ nhiều bảng; WHERE chỉ chứa điều kiện từ câu hỏi hoặc cần để join.
- Truy vấn phải dựa hoàn toàn trên thông tin cung cấp; phân tích chi tiết cột cho thống kê, loại bỏ bản ghi không hợp lệ nếu cần.
- Có thể bổ sung điều kiện về thời gian dựa vào ngày hiện tại nếu cần.
- Sau khi sinh truy vấn xong, dừng luôn, không cần giải thích thêm.
- Phân tích chi tiết ý định người dùng và câu hỏi để lựa chọn chính xác phép toán phân tích như COUNT, SUM phù hợp.
- Phân tích chi tiết câu hỏi hiện tại là hỏi về hệ thống nào và không được phép sử dụng trường thông tin của hệ thống khác.
- Mỗi câu hỏi đề chỉ hỏi về một hệ thống, khi truy vấn dữ liệu cần tra từ bảng ticket cụ thể của từng hệ thống.
- Chú ý vào câu hỏi hiện tại để phân tích xem nó liên quan tới câu nào trong quá khứ (nếu có)
- **Nếu thông tin không đủ rõ ràng hoặc không thể xác định chính xác bảng, cột, bạn có thể tạo các câu hỏi phụ để làm rõ ý định người dùng trước khi sinh truy vấn SQL.**
- Chú ý bọc dấu ngoặc cho các phần tử con trong phép UNION

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

- Một số câu hỏi - trả lời ví dụ:
{ex_str}

- **Câu hỏi hiện tại**:
{state["question"]}
""".strip()
    
    state["sql_query"] = get_sql_res(prompt)
    state["validated"] = False
    
    return state

if __name__ == "__main__":
    # Mock state với dữ liệu mẫu
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
        "examples": [
            {
                "question": "Số ticket SC tạo hôm nay",
                "answer": (
                    "SELECT COUNT(*)\n"
                    "FROM fact_sc_tickets s\n"
                    "JOIN fact_tickets t ON s.ticket_id = t.id\n"
                    "JOIN fact_ticket_creation c ON t.creation_id = c.id\n"
                    "WHERE c.\"date\" = TRUNC(SYSDATE)"
                )
            }
        ]
    }

    # Gọi hàm gen_sql
    updated_state = gen_sql(test_state)

    print("Generated SQL Query:")
    print(updated_state.get("sql_query"))
    print("\nValidated:", updated_state.get("validated"))