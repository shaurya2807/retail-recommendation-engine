from app.models.product import Product, ProductCreate


class ProductRepository:
    def get_by_id(self, product_id: int) -> Product | None:
        raise NotImplementedError

    def get_by_ids(self, ids: list[int]) -> list[Product]:
        raise NotImplementedError

    def get_all(self, limit: int = 100, offset: int = 0) -> list[Product]:
        raise NotImplementedError

    def create(self, product: ProductCreate) -> Product:
        raise NotImplementedError
