from fastapi import APIRouter

from app.api import products, recommendations, users

router = APIRouter()
router.include_router(products.router, prefix="/products", tags=["products"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
