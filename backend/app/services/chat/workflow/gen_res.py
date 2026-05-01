from app.services.chat.workflow.graph_state import GraphState
from app.services.chat.bot import get_res

def _results_to_markdown(results, max_rows=20):
    if not results:
        return "No data"

    columns = list(results[0].keys())

    # header
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |"

    lines = [header, separator]

    # rows
    for row in results[:max_rows]:
        values = []
        for col in columns:
            v = row.get(col, "")
            v = str(v).replace("\n", " ")  # tránh vỡ format
            values.append(v)
        lines.append("| " + " | ".join(values) + " |")

    # truncate notice
    if len(results) > max_rows:
        lines.append(f"\n... ({len(results) - max_rows} more rows)")

    return "\n".join(lines)

def gen_res(state: GraphState):
    if not state["validated"]:
        return state

    results_str = _results_to_markdown(state["results"])

    more_info = ""
    for table in state["schema"]:
        for column in table["columns"]:
            column_name = column["column_name"]
            column_comment = column["column_comment"]
            if column_name in state["sql_query"]:
                more_info += f"(Column){column_name}: {column_comment}\n"

    prompt = f"""
Bạn là một trợ lý dữ liệu chuyên nghiệp. Nhiệm vụ của bạn là **tạo câu trả lời rõ ràng, chính xác và dễ hiểu cho người dùng** dựa trên kết quả truy vấn SQL.


Đầu vào gồm:
- **Câu hỏi hiện tại của người dùng**
- **Truy vấn SQL đã thực thi**
- **Tổng số bản ghi tìm thấy**
- **Kết quả truy vấn** (có thể đã bị cắt bớt nếu quá dài)
- **Thông tin bổ sung (nếu có)**


Yêu cầu khi tạo câu trả lời:
- Trả lời trực tiếp vào câu hỏi, dựa trên kết quả truy vấn.
- Tóm tắt kết quả một cách ngắn gọn, dễ hiểu, đúng trọng tâm.
- Nếu số lượng bản ghi ít:
   + Có thể liệt kê chi tiết từng dòng.
- Nếu số lượng bản ghi nhiều:
   + Tóm tắt xu hướng chính, không liệt kê toàn bộ.
- Sử dụng tên cột để diễn giải thành ngôn ngữ tự nhiên, dễ hiểu cho người dùng.
- Không hiển thị SQL trong câu trả lời.
- Không suy diễn ngoài dữ liệu được cung cấp.
- Nếu không có kết quả:
   + Trả lời rõ ràng rằng không tìm thấy dữ liệu phù hợp.
- Nếu dữ liệu bị cắt:
   + Nói rõ đây là kết quả một phần.
- Có thể sử dụng thông tin bổ sung để làm rõ câu trả lời nếu cần.
- Giữ giọng văn chuyên nghiệp, dễ hiểu.
- Không thêm thông tin không có trong dữ liệu.
- Không giải thích cách truy vấn hay logic SQL.

Thông tin đầu vào:
- **Câu hỏi**:
{state["question"]}

- **Truy vấn SQL**:
{state["sql_query"]}

- **Tổng số bản ghi**:
{len(state["results"])}

- **Kết quả truy vấn**:
{results_str}

- **Thông tin bổ sung**:
{more_info}
""".strip()
    
    state["answer"] = get_res(prompt)
    return state

if __name__ == "__main__":
    # ---------- Mock get_res để test offline ----------
    def mock_get_res(prompt):
        return "Có 42 ticket sự cố được tạo trong ngày hôm qua."

    import app.services.chat.bot as bot
    bot.get_res = mock_get_res   # Ghi đè tạm thời

    # ---------- Chuẩn bị state ----------
    test_state = {
        "question": "Số lượng ticket SC hôm qua",
        "sql_query": (
            "SELECT COUNT(*) AS cnt\n"
            "FROM fact_sc_tickets s\n"
            "JOIN fact_tickets t ON s.ticket_id = t.id\n"
            "JOIN fact_ticket_creation c ON t.creation_id = c.id\n"
            "WHERE c.\"date\" = TRUNC(SYSDATE)-1"
        ),
        "validated": True,
        "results": [{"CNT": 42}],   # Kết quả giả lập
        "schema": [
            {"table_name": "FACT_SC_TICKETS",
             "columns": [
                 {"column_name": "TICKET_ID", "column_comment": "ID ticket"},
                 {"column_name": "SC_KHG_STATUS", "column_comment": "Trạng thái ảnh hưởng KH (Có/Không)"},
             ]},
            {"table_name": "FACT_TICKET_CREATION",
             "columns": [
                 {"column_name": "date", "column_comment": "Ngày khởi tạo"},
             ]}
        ]
    }

    # ---------- Chạy hàm ----------
    updated_state = gen_res(test_state)

    print("Câu trả lời được sinh ra:")
    print(updated_state.get("answer"))

    # ---------- Test trường hợp validated=False ----------
    invalid_state = {"validated": False, "answer": None}
    gen_res(invalid_state)
    print("\nKhi validated=False, answer vẫn None:", invalid_state.get("answer") is None)