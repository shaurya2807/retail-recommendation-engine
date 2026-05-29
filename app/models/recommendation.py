from pydantic import BaseModel

from app.models.product import Product


class RecommendationResult(BaseModel):
    user_id: int
    products: list[Product]
    model_version: str
    score_map: dict[int, float] = {}
