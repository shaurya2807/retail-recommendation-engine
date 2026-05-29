from fastapi import FastAPI

from configs.config import settings
from app.api import router as api_router

app = FastAPI(
    title="Retail Recommendation Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["system"])
def health_check() -> dict:
    return {"status": "ok", "env": settings.app_env}
