from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.projects import router as projects_router
from app.core.config import get_settings
from app.core.logging_config import configure_logging
from app.core.request_logging import RequestLoggingMiddleware

settings = get_settings()

configure_logging()

app = FastAPI(
    title=settings.name,
    version=settings.version,
    description="An AI-powered engineering knowledge platform.",
)

app.add_middleware(RequestLoggingMiddleware)
app.include_router(health_router)
app.include_router(projects_router)


@app.get("/api/v1/version")
def get_version() -> dict[str, str]:
    return {
        "application": settings.name,
        "version": settings.version,
    }
