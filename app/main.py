from fastapi import FastAPI

from app.api.routes.health import router as health_router

app = FastAPI(
    title="AI Engineering Platform",
    version="0.1.0",
    description="An AI-powered engineering knowledge platform.",
)

app.include_router(health_router)


@app.get("/api/v1/version")
def get_version() -> dict[str, str]:
    return {
        "application": "AI Engineering Platform",
        "version": "0.1.0",
    }
