from __future__ import annotations

from collections import defaultdict

import numpy as np
import pandas as pd

from app.ml.trainer import CollaborativeFilteringTrainer
from app.repository.interaction_repo import InteractionRepository, _WEIGHTS


class RecommendationEvaluator:
    """Offline evaluation of recommendation models."""

    # ------------------------------------------------------------------
    # Per-user ranking metrics
    # ------------------------------------------------------------------

    @staticmethod
    def precision_at_k(recommended: list[int], relevant: set[int], k: int) -> float:
        top_k = recommended[:k]
        return sum(1 for r in top_k if r in relevant) / k if k > 0 else 0.0

    @staticmethod
    def recall_at_k(recommended: list[int], relevant: set[int], k: int) -> float:
        if not relevant:
            return 0.0
        top_k = recommended[:k]
        return sum(1 for r in top_k if r in relevant) / len(relevant)

    @staticmethod
    def ndcg_at_k(recommended: list[int], relevant: set[int], k: int) -> float:
        top_k = recommended[:k]
        dcg  = sum(1.0 / np.log2(i + 2) for i, r in enumerate(top_k) if r in relevant)
        ideal_len = min(len(relevant), k)
        idcg = sum(1.0 / np.log2(i + 2) for i in range(ideal_len))
        return dcg / idcg if idcg > 0 else 0.0

    # ------------------------------------------------------------------
    # Leave-one-out evaluation
    # ------------------------------------------------------------------

    def evaluate_model(
        self,
        trainer: CollaborativeFilteringTrainer,
        interaction_repo: InteractionRepository,
        k: int = 10,
    ) -> dict[str, float]:
        """Leave-one-out evaluation across all users.

        For each user with ≥ 2 interactions, hold out the chronologically
        last interaction as ground truth, fit a fresh model on the remainder,
        and compute precision@k, recall@k, and nDCG@k.  Returns means.
        """
        interactions = interaction_repo.get_all()
        if not interactions:
            return {"precision_at_k": 0.0, "recall_at_k": 0.0, "ndcg_at_k": 0.0}

        # Sort each user's interactions chronologically
        user_ixs: dict[int, list] = defaultdict(list)
        for ix in interactions:
            user_ixs[ix.user_id].append(ix)
        for uid in user_ixs:
            user_ixs[uid].sort(key=lambda x: x.created_at)

        # Split: training set vs held-out item per user
        held_out: dict[int, int] = {}
        train_records: list[dict] = []

        for uid, ixs in user_ixs.items():
            if len(ixs) < 2:
                continue
            held_out[uid] = ixs[-1].product_id
            for ix in ixs[:-1]:
                val = ix.rating if ix.rating is not None else _WEIGHTS[ix.interaction_type]
                train_records.append(
                    {"user_id": ix.user_id, "product_id": ix.product_id, "value": val}
                )

        if not held_out:
            return {"precision_at_k": 0.0, "recall_at_k": 0.0, "ndcg_at_k": 0.0}

        # Build wide interaction matrix from training records
        df  = pd.DataFrame(train_records)
        agg = df.groupby(["user_id", "product_id"])["value"].max().reset_index()
        train_matrix = (
            agg.pivot(index="user_id", columns="product_id", values="value")
            .fillna(0)
        )
        train_matrix.columns.name = None
        train_matrix.index.name   = None

        # Fit a fresh trainer on leave-one-out data
        eval_trainer = CollaborativeFilteringTrainer(
            n_components=trainer.n_components,
            random_state=trainer.random_state,
        )
        eval_trainer.fit(train_matrix)

        # Score each user whose held-out item is predictable
        precision_vals: list[float] = []
        recall_vals:    list[float] = []
        ndcg_vals:      list[float] = []

        for uid, held_product in held_out.items():
            if uid not in eval_trainer._user_index:
                continue
            recommended = eval_trainer.predict(uid, top_n=k)
            relevant    = {held_product}
            precision_vals.append(self.precision_at_k(recommended, relevant, k))
            recall_vals.append(self.recall_at_k(recommended, relevant, k))
            ndcg_vals.append(self.ndcg_at_k(recommended, relevant, k))

        n = len(precision_vals)
        if n == 0:
            return {"precision_at_k": 0.0, "recall_at_k": 0.0, "ndcg_at_k": 0.0}

        return {
            "precision_at_k": float(np.mean(precision_vals)),
            "recall_at_k":    float(np.mean(recall_vals)),
            "ndcg_at_k":      float(np.mean(ndcg_vals)),
        }
