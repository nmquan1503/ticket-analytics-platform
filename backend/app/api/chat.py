from fastapi import APIRouter

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

@router.post("/")
def chat_root():
    return {
        "message": "hello. this is chat router"
    }