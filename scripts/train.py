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

MODEL_NAME = "collaborative_filter"
MODEL_VERSION = "1.0"


def main() -> None:
    interaction_repo = InteractionRepository()
    registry = ModelRegistry(repo=ModelRegistryRepository())

    # ── 1. Load interaction matrix ─────────────────────────────────────────
    print("Loading interaction matrix …")
    matrix = interaction_repo.get_interaction_matrix()
    if matrix.empty:
        print("No interactions found. Run scripts/seed.py first.", file=sys.stderr)
        sys.exit(1)
    print(f"  shape : {matrix.shape[0]} users × {matrix.shape[1]} products")
    nonzero = int((matrix.values > 0).sum())
    print(f"  non-zero cells : {nonzero}  ({nonzero / matrix.size * 100:.1f}% density)")

    # ── 2. Fit model on full data ──────────────────────────────────────────
    print("\nFitting collaborative filtering model (TruncatedSVD, n_components=20) …")
    trainer = CollaborativeFilteringTrainer(n_components=20)
    trainer.fit(matrix)
    actual_k = trainer._user_factors.shape[1]
    print(f"  effective n_components : {actual_k}")

    # ── 3. Leave-one-out evaluation ────────────────────────────────────────
    print("\nRunning leave-one-out evaluation (k=10) …")
    evaluator = RecommendationEvaluator()
    metrics = evaluator.evaluate_model(trainer, interaction_repo, k=10)

    print("\nMetrics @ k=10")
    print(f"  precision@10 : {metrics['precision_at_k']:.4f}")
    print(f"  recall@10    : {metrics['recall_at_k']:.4f}")
    print(f"  ndcg@10      : {metrics['ndcg_at_k']:.4f}")

    # ── 4. Save to registry ────────────────────────────────────────────────
    print(f"\nSaving model to registry as '{MODEL_NAME}' v{MODEL_VERSION} …")
    record = registry.save(
        trainer=trainer,
        model_name=MODEL_NAME,
        version=MODEL_VERSION,
        metrics=metrics,
    )
    print(f"  DB id        : {record.id}")
    print(f"  model path   : {record.model_path}")
    print(f"  active       : {record.is_active}")
    print("\nDone.")


if __name__ == "__main__":
    main()
