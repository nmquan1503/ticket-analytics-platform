import uuid
import csv
import os
from pathlib import Path
from app.services.chat.workflow.graph_state import GraphState
from app.services.chat.workflow.workflow import build_workflow
from app.db.oracle_client import db_client
from app.config import settings

class ChatService:
    def __init__(self):
        self.workflow = build_workflow()

    def process_question(self, question: str) -> dict:
        if question.lower().startswith("select "):
            try:
                answer = ""
                results = db_client.fetch_all(question)
            except Exception as e:
                answer = str(e)
                results = None
        else:
            initial_state = {"question": question}
            result_state = self.workflow.invoke(initial_state)
            answer = result_state["answer"]
            results = result_state["results"]

        file_id = None
        if results:
            file_id = self._save_csv(results)

        return {"answer": answer, "file_id": file_id}

    def _save_csv(self, rows: list[dict]) -> str:
        if not rows:
            return None
        file_id = str(uuid.uuid4())
        file_path = Path(settings.CSV_DIR) / f"{file_id}.csv"

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        return file_id