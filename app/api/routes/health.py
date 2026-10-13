from fastapi import APIRouter

router = APIRouter()


@router.get("/health/live")
def liveness_check() -> dict[str, str]:
    return {"status": "alive"}
