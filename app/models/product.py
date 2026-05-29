from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class ProductBase(BaseModel):
    sku: str
    name: str
    category: str
    subcategory: str | None = None
    price: Decimal
    description: str | None = None


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
