from contextlib import asynccontextmanager

import joblib
from fastapi import FastAPI, Request

from app.api import router as api_router
from app.repository.model_registry_repo import ModelRegistryRepository
from configs.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load all active ML models into app.state once on boot.

    Tolerates an unavailable database or missing model files so the server
    can still start (endpoints will return 503 until models are trained).
    """
    repo = ModelRegistryRepository()
    for key in ("hybrid", "content_based"):
        record = None
        model  = None
        try:
            record = repo.get_active_model(key)
            if record:
                model = joblib.load(record.model_path)
        except Exception:
            pass
        setattr(app.state, key, model)
        setattr(app.state, f"{key}_record", record)
    yield
    # No cleanup needed for in-memory models.


app = FastAPI(
    title="Retail Recommendation Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["system"])
def health_check(request: Request) -> dict:
    def _status(key: str) -> str:
        return "loaded" if getattr(request.app.state, key, None) is not None else "not_loaded"

    return {
        "status": "ok",
        "env": settings.app_env,
        "models": {
            "hybrid":        _status("hybrid"),
            "content_based": _status("content_based"),
        },
    }
