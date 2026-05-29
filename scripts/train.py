"""Training entry point: fit, evaluate, and register the collaborative filter."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ml.evaluator import RecommendationEvaluator           # noqa: E402
from app.ml.registry import ModelRegistry                       # noqa: E402
from app.ml.trainer import CollaborativeFilteringTrainer        # noqa: E402
from app.repository.interaction_repo import InteractionRepository  # noqa: E402
from app.repository.model_registry_repo import ModelRegistryRepository  # noqa: E402
from app.ml.content_based import ContentBasedRecommender                # noqa: E402
from app.ml.hybrid import HybridRecommender                             # noqa: E402
from app.repository.product_repo import ProductRepository               # noqa: E402

MODEL_NAME = "collaborative_filter"
MODEL_VERSION = "1.0"
CB_MODEL_NAME    = "content_based"
CB_MODEL_VERSION = "1.0"
HY_MODEL_NAME    = "hybrid"
HY_MODEL_VERSION = "1.0"


def main() -> None:
    interaction_repo = InteractionRepository()
    registry = ModelRegistry(repo=ModelRegistryRepository())

    # ── 1. Load interaction matrix ─────────────────────────────────────────
    print("Loading interaction matrix ...")
    matrix = interaction_repo.get_interaction_matrix()
    if matrix.empty:
        print("No interactions found. Run scripts/seed.py first.", file=sys.stderr)
        sys.exit(1)
    print(f"  shape : {matrix.shape[0]} users × {matrix.shape[1]} products")
    nonzero = int((matrix.values > 0).sum())
    print(f"  non-zero cells : {nonzero}  ({nonzero / matrix.size * 100:.1f}% density)")

    # ── 2. Fit model on full data ──────────────────────────────────────────
    print("\nFitting collaborative filtering model (TruncatedSVD, n_components=20) ...")
    trainer = CollaborativeFilteringTrainer(n_components=20)
    trainer.fit(matrix)
    actual_k = trainer._user_factors.shape[1]
    print(f"  effective n_components : {actual_k}")

    # ── 3. Leave-one-out evaluation ────────────────────────────────────────
    print("\nRunning leave-one-out evaluation (k=10) ...")
    evaluator = RecommendationEvaluator()
    metrics = evaluator.evaluate_model(trainer, interaction_repo, k=10)

    print("\nMetrics @ k=10")
    print(f"  precision@10 : {metrics['precision_at_k']:.4f}")
    print(f"  recall@10    : {metrics['recall_at_k']:.4f}")
    print(f"  ndcg@10      : {metrics['ndcg_at_k']:.4f}")

    # ── 4. Save to registry ────────────────────────────────────────────────
    print(f"\nSaving model to registry as '{MODEL_NAME}' v{MODEL_VERSION} ...")
    record = registry.save(
        trainer=trainer,
        model_name=MODEL_NAME,
        version=MODEL_VERSION,
        metrics=metrics,
    )
    print(f"  DB id        : {record.id}")
    print(f"  model path   : {record.model_path}")
    print(f"  active       : {record.is_active}")

    # ── 5. Content-based recommender ──────────────────────────────────────
    print("\nFitting content-based recommender (TF-IDF, max_features=500) ...")
    products = ProductRepository().get_all()
    products_data = [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "subcategory": p.subcategory,
            "description": p.description,
        }
        for p in products
    ]
    cb_model = ContentBasedRecommender()
    cb_model.fit(products_data)
    print(f"  {len(products_data)} products indexed")

    cb_record = registry.save(
        trainer=cb_model,
        model_name=CB_MODEL_NAME,
        version=CB_MODEL_VERSION,
        metrics={},
    )
    print(f"  Saved as '{CB_MODEL_NAME}' v{CB_MODEL_VERSION}  [active]  (DB id={cb_record.id})")

    # ── 6. Hybrid recommender ─────────────────────────────────────────────
    hybrid_model = HybridRecommender(collab=trainer, content=cb_model)
    print(
        f"\nBuilding hybrid recommender "
        f"(w_collab={hybrid_model._collab_weight}, w_content={hybrid_model._content_weight}) ..."
    )

    hy_record = registry.save(
        trainer=hybrid_model,
        model_name=HY_MODEL_NAME,
        version=HY_MODEL_VERSION,
        metrics={},
    )
    print(f"  Saved as '{HY_MODEL_NAME}' v{HY_MODEL_VERSION}  [active]  (DB id={hy_record.id})")

    # ── 7. Sample prediction for user_id=1 ────────────────────────────────
    sample_user_id = 1
    print(f"\nSample top-10 hybrid recommendations — user_id={sample_user_id}")
    if sample_user_id in matrix.index:
        user_row       = matrix.loc[sample_user_id]
        interacted_ids = [int(pid) for pid in user_row[user_row > 0].index]
    else:
        interacted_ids = []
    print(f"  already interacted with {len(interacted_ids)} products")

    rec_ids = hybrid_model.predict(
        user_id=sample_user_id,
        user_interacted_product_ids=interacted_ids,
        top_n=10,
    )

    product_map = {p.id: p.name for p in products}
    print()
    for rank, pid in enumerate(rec_ids, 1):
        print(f"  {rank:>2}. [{pid:>3}] {product_map.get(pid, 'unknown')}")

    print("\nDone.")


if __name__ == "__main__":
    main()
