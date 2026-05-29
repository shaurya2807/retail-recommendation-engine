from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class ModelVersionInfo(BaseModel):
    model_config = {"from_attributes": True}

    model_name: str
    version: str
    metrics: dict
    is_active: bool
    created_at: datetime


class ModelsListResponse(BaseModel):
    models: list[ModelVersionInfo]


class RecommendedItem(BaseModel):
    rank: int
    product_id: int
    sku: str
    name: str
    category: str
    price: Decimal
    score: float


class RecommendationResponse(BaseModel):
    user_id: int
    recommendations: list[RecommendedItem]
    model_version: str
    model_name: str


class SimilarProductsResponse(BaseModel):
    product_id: int
    similar: list[RecommendedItem]
    model_name: str
    model_version: str
