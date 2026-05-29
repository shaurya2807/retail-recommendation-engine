from __future__ import annotations

import joblib
import numpy as np

from app.ml.content_based import ContentBasedRecommender
from app.ml.trainer import CollaborativeFilteringTrainer
from configs.config import settings


def _normalize_01(arr: np.ndarray) -> np.ndarray:
    """Min-max scale to [0, 1]; returns a uniform 0.5 array when all values are equal."""
    lo, hi = float(arr.min()), float(arr.max())
    if hi == lo:
        return np.full_like(arr, 0.5, dtype=np.float64)
    return (arr - lo) / (hi - lo)


class HybridRecommender:
    """Weighted linear combination of collaborative-filter and content-based scores.

    Weights default to settings.collab_weight / settings.content_weight but can
    be overridden at construction time for experimentation.
    """

    def __init__(
        self,
        collab: CollaborativeFilteringTrainer,
        content: ContentBasedRecommender,
        collab_weight: float | None = None,
        content_weight: float | None = None,
    ) -> None:
        self._collab  = collab
        self._content = content
        self._collab_weight  = collab_weight  if collab_weight  is not None else settings.collab_weight
        self._content_weight = content_weight if content_weight is not None else settings.content_weight

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def _rank_all(
        self,
        user_id: int,
        user_interacted_product_ids: list[int],
        top_n: int,
    ) -> list[tuple[int, float]]:
        """Return (product_id, hybrid_score) pairs, excluding seen products."""
        collab_map  = self._collab.raw_scores(user_id)
        content_map = self._content.score_all_for_user(user_interacted_product_ids)

        all_pids = sorted(set(collab_map) | set(content_map))
        if not all_pids:
            return []

        collab_arr  = np.array([collab_map.get(pid,  0.0) for pid in all_pids])
        content_arr = np.array([content_map.get(pid, 0.0) for pid in all_pids])

        collab_arr  = _normalize_01(collab_arr)
        content_arr = _normalize_01(content_arr)

        hybrid = self._collab_weight * collab_arr + self._content_weight * content_arr

        seen = set(user_interacted_product_ids)
        ranked = sorted(
            (
                (pid, float(hybrid[i]))
                for i, pid in enumerate(all_pids)
                if pid not in seen
            ),
            key=lambda x: x[1],
            reverse=True,
        )
        return ranked[:top_n]

    def predict(
        self,
        user_id: int,
        user_interacted_product_ids: list[int],
        top_n: int = 10,
    ) -> list[int]:
        """Return top_n product IDs by weighted hybrid score."""
        return [pid for pid, _ in self._rank_all(user_id, user_interacted_product_ids, top_n)]

    def predict_with_scores(
        self,
        user_id: int,
        user_interacted_product_ids: list[int],
        top_n: int = 10,
    ) -> list[tuple[int, float]]:
        """Return (product_id, score) pairs for the top_n hybrid recommendations."""
        return self._rank_all(user_id, user_interacted_product_ids, top_n)

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def save(self, path: str) -> None:
        joblib.dump(self, path)

    @classmethod
    def load(cls, path: str) -> HybridRecommender:
        return joblib.load(path)
