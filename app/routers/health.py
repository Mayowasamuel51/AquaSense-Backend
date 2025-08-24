from fastapi import APIRouter

router = APIRouter()

@router.get("/he")
def health():
    return {"status": "ok"}