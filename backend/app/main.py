from fastapi import FastAPI
from app.api.sc_analytics import router as sc_analytics_router
from app.api.ht_analytics import router as ht_analytics_router
from app.api.chat import router as chat_router

app = FastAPI(title="Oracle Dashboard Backend")

app.include_router(sc_analytics_router)
app.include_router(ht_analytics_router)
app.include_router(chat_router)