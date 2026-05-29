from fastapi import APIRouter, HTTPException, Query, Request

from app.models.recommendation import (
    RecommendationResponse,
    RecommendedItem,
    SimilarProductsResponse,
)
from app.repository.interaction_repo import InteractionRepository
from app.repository.product_repo import ProductRepository
from app.repository.user_repo import UserRepository

router = APIRouter()


# NOTE: /similar/{product_id} must be registered before /{user_id} so that
# the literal segment "similar" is not swallowed as an integer user_id.

@router.get("/similar/{product_id}", response_model=SimilarProductsResponse)
def similar_products(
    product_id: int,
    request: Request,
    top_n: int = Query(10, ge=1, le=100),
):
    """Return products most similar to product_id via TF-IDF cosine similarity."""
    cb        = request.app.state.content_based
    cb_record = request.app.state.content_based_record

    if cb is None:
        raise HTTPException(status_code=503, detail="Model not trained yet")

    product_repo = ProductRepository()
    if product_repo.get_by_id(product_id) is None:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")

    scored   = cb.predict_with_scores(product_id, top_n)
    pid_list = [pid for pid, _ in scored]
    products = {p.id: p for p in product_repo.get_by_ids(pid_list)} if pid_list else {}

    similar = [
        RecommendedItem(
            rank=rank,
            product_id=pid,
            sku=products[pid].sku,
            name=products[pid].name,
            category=products[pid].category,
            price=products[pid].price,
            score=round(score, 4),
        )
        for rank, (pid, score) in enumerate(scored, 1)
        if pid in products
    ]

    return SimilarProductsResponse(
        product_id=product_id,
        similar=similar,
        model_name=cb_record.model_name,
        model_version=cb_record.version,
    )


@router.get("/{user_id}", response_model=RecommendationResponse)
def recommend_for_user(
    user_id: int,
    request: Request,
    top_n: int = Query(10, ge=1, le=100),
):
    """Return personalised hybrid recommendations for a user."""
    hybrid        = request.app.state.hybrid
    hybrid_record = request.app.state.hybrid_record

    if hybrid is None:
        raise HTTPException(status_code=503, detail="Model not trained yet")

    if UserRepository().get_by_id(user_id) is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    interactions   = InteractionRepository().get_by_user_id(user_id)
    interacted_ids = list({ix.product_id for ix in interactions})

    scored   = hybrid.predict_with_scores(user_id, interacted_ids, top_n)
    pid_list = [pid for pid, _ in scored]
    products = {p.id: p for p in ProductRepository().get_by_ids(pid_list)} if pid_list else {}

    recommendations = [
        RecommendedItem(
            rank=rank,
            product_id=pid,
            sku=products[pid].sku,
            name=products[pid].name,
            category=products[pid].category,
            price=products[pid].price,
            score=round(score, 4),
        )
        for rank, (pid, score) in enumerate(scored, 1)
        if pid in products
    ]

    return RecommendationResponse(
        user_id=user_id,
        recommendations=recommendations,
        model_version=hybrid_record.version,
        model_name=hybrid_record.model_name,
    )
