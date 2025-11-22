from fastapi import APIRouter
from app.core.config import settings
from app.api.v1.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        app=settings.APP_NAME,
        version=settings.APP_VERSION,
        status="healthy",
        debug=settings.DEBUG
    )
