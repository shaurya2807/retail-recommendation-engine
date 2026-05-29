from app.models.recommendation import RecommendationResult
from app.repository.interaction_repo import InteractionRepository
from app.repository.model_registry_repo import ModelRegistryRepository
from app.repository.product_repo import ProductRepository


class RecommendationService:
    def __init__(
        self,
        interaction_repo: InteractionRepository,
        product_repo: ProductRepository,
        model_repo: ModelRegistryRepository,
    ) -> None:
        self._interactions = interaction_repo
        self._products = product_repo
        self._models = model_repo

    def recommend_for_user(self, user_id: int, top_k: int = 10) -> RecommendationResult:
        raise NotImplementedError
