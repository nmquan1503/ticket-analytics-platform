from fastapi import APIRouter

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

@router.get("/")
def analytics_root():
    return {
        "message": "hello. this is analytic router"
    }