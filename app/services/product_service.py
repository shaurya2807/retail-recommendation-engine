from app.models.product import Product, ProductCreate
from app.repository.product_repo import ProductRepository


class ProductService:
    def __init__(self, repo: ProductRepository) -> None:
        self._repo = repo

    def get_product(self, product_id: int) -> Product | None:
        raise NotImplementedError

    def list_products(self, limit: int = 100, offset: int = 0) -> list[Product]:
        raise NotImplementedError

    def create_product(self, data: ProductCreate) -> Product:
        raise NotImplementedError
