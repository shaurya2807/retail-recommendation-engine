from fastapi import APIRouter

from app.models.recommendation import ModelVersionInfo, ModelsListResponse
from app.repository.model_registry_repo import ModelRegistryRepository

router = APIRouter()

_MODEL_NAMES = ["collaborative_filter", "content_based", "hybrid"]


@router.get("/", response_model=ModelsListResponse)
def list_models():
    """List all registered model versions with their metrics and active status."""
    repo = ModelRegistryRepository()
    records = []
    for name in _MODEL_NAMES:
        records.extend(repo.list_versions(name))
    records.sort(key=lambda r: r.created_at, reverse=True)
    return ModelsListResponse(
        models=[ModelVersionInfo.model_validate(r) for r in records]
    )
