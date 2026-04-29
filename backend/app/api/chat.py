from fastapi import APIRouter
from fastapi.responses import FileResponse
import os
import uuid
import csv

router = APIRouter(prefix="/chat", tags=["Chat"])

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)


# =========================
# 1. CHAT API
# =========================
@router.post("/")
def chat():
    """
    Chatbot API:
    - trả message
    - tạo CSV file
    - trả file_id để download
    """

    file_id = str(uuid.uuid4())
    filename = f"{file_id}.csv"
    file_path = os.path.join(DATA_DIR, filename)

    # demo data (replace bằng logic Oracle / AI / SQL của bạn)
    rows = [
        ["id", "ticket", "status"],
        [1, "TICKET-001", "OPEN"],
        [2, "TICKET-002", "CLOSED"],
        [3, "TICKET-003", "PROCESSING"],
    ]

    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    return {
        "message": "Đây là kết quả từ chatbot",
        "file_id": file_id
    }


# =========================
# 2. DOWNLOAD API
# =========================
@router.get("/download/{file_id}")
def download(file_id: str):
    """
    Download CSV file theo file_id
    """

    file_path = os.path.join(DATA_DIR, f"{file_id}.csv")

    if not os.path.exists(file_path):
        return {"error": "file not found"}

    return FileResponse(
        path=file_path,
        media_type="text/csv",
        filename=f"{file_id}.csv"
    )