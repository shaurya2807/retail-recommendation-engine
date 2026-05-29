from fastapi import APIRouter, HTTPException, Query

from app.models.product import Product
from app.repository.product_repo import ProductRepository

router = APIRouter()


# NOTE: /category/{category} is defined before /{product_id} so that the
# literal segment "category" is not misrouted. FastAPI's int converter
# already prevents "category" matching /{product_id: int}, but explicit
# ordering makes intent clear.

@router.get("/", response_model=list[Product])
def list_products(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return ProductRepository().get_all(limit=limit, offset=offset)


@router.get("/category/{category}", response_model=list[Product])
def products_by_category(category: str):
    return ProductRepository().get_by_category(category)


@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int):
    product = ProductRepository().get_by_id(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return product
