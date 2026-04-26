from fastapi import FastAPI
from app.api.analytics import router as analytics_router
from app.api.chat import router as chat_router

app = FastAPI(title="Oracle Dashboard Backend")

app.include_router(analytics_router)
app.include_router(chat_router)