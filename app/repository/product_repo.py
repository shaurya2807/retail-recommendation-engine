from app.models.product import Product, ProductCreate
from app.repository.db import db_cursor


class ProductRepository:
    def get_all(self, limit: int = 100, offset: int = 0) -> list[Product]:
        with db_cursor() as cur:
            cur.execute(
                "SELECT id, sku, name, category, subcategory, price, description, created_at"
                " FROM products ORDER BY id LIMIT %s OFFSET %s",
                (limit, offset),
            )
            return [Product(**dict(row)) for row in cur.fetchall()]

    def get_by_id(self, product_id: int) -> Product | None:
        with db_cursor() as cur:
            cur.execute(
                "SELECT id, sku, name, category, subcategory, price, description, created_at"
                " FROM products WHERE id = %s",
                (product_id,),
            )
            row = cur.fetchone()
        return Product(**dict(row)) if row else None

    def get_by_category(self, category: str) -> list[Product]:
        with db_cursor() as cur:
            cur.execute(
                "SELECT id, sku, name, category, subcategory, price, description, created_at"
                " FROM products WHERE category = %s ORDER BY name",
                (category,),
            )
            return [Product(**dict(row)) for row in cur.fetchall()]

    def get_by_ids(self, ids: list[int]) -> list[Product]:
        if not ids:
            return []
        with db_cursor() as cur:
            cur.execute(
                "SELECT id, sku, name, category, subcategory, price, description, created_at"
                " FROM products WHERE id = ANY(%s) ORDER BY id",
                (ids,),
            )
            return [Product(**dict(row)) for row in cur.fetchall()]

    def create(self, product: ProductCreate) -> Product:
        raise NotImplementedError
