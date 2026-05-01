from fastapi import APIRouter
from fastapi.responses import FileResponse
import os
import uuid
import csv
from app.services.chat.service import ChatService
from app.schemas.chat import ChatRequest
from app.config import settings
from pathlib import Path

sv = ChatService()

router = APIRouter(prefix="/chat", tags=["Chat"])

# =========================
# 1. CHAT API
# =========================
@router.post("/")
def chat(request: ChatRequest):
    results = sv.process_question(request.question)
    return {
        "message": results["answer"],
        "file_id": results["file_id"]
    }

@router.get("/download/{file_id}")
def download(file_id: str):
    """
    Download CSV file theo file_id
    """

    file_path = Path(settings.CSV_DIR) / f"{file_id}.csv"

    if not os.path.exists(file_path):
        return {"error": "file not found"}

    return FileResponse(
        path=file_path,
        media_type="text/csv",
        filename=f"{file_id}.csv"
    )