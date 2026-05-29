from __future__ import annotations

import numpy as np
import pandas as pd
import joblib
from sklearn.decomposition import TruncatedSVD


class CollaborativeFilteringTrainer:
    """SVD-based collaborative filtering on a user × product interaction matrix."""

    def __init__(self, n_components: int = 20, random_state: int = 42) -> None:
        self.n_components = n_components
        self.random_state = random_state
        self._svd: TruncatedSVD | None = None
        self._user_factors: np.ndarray | None = None   # (n_users, k)
        self._item_factors: np.ndarray | None = None   # (n_items, k)
        self._user_index: dict[int, int] = {}          # user_id  → row index
        self._item_ids: list[int] = []                 # col index → product_id
        self._matrix: np.ndarray | None = None         # raw interaction matrix

    # ------------------------------------------------------------------
    # Fitting
    # ------------------------------------------------------------------

    def fit(self, matrix: pd.DataFrame) -> CollaborativeFilteringTrainer:
        """Decompose a user × product interaction matrix with TruncatedSVD.

        Args:
            matrix: Wide-format DataFrame whose index is user_ids and whose
                    columns are product_ids.  Values are interaction scores
                    (0 = no interaction).
        """
        self._user_index = {int(uid): i for i, uid in enumerate(matrix.index)}
        self._item_ids   = [int(pid) for pid in matrix.columns]

        self._matrix = matrix.to_numpy(dtype=np.float64)

        # sklearn requires n_components < min(n_rows, n_cols)
        n_components = min(self.n_components, min(self._matrix.shape) - 1)

        self._svd = TruncatedSVD(n_components=n_components, random_state=self.random_state)
        self._user_factors = self._svd.fit_transform(self._matrix)  # (n_users, k)
        self._item_factors = self._svd.components_.T                 # (n_items, k)
        return self

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def predict(self, user_id: int, top_n: int = 10) -> list[int]:
        """Return up to top_n product IDs not yet interacted with, ranked by score."""
        if self._user_factors is None:
            raise RuntimeError("Model has not been fitted. Call fit() first.")

        user_idx = self._user_index.get(user_id)
        if user_idx is None:
            return []

        # Predicted affinity for all items
        user_vec = self._user_factors[user_idx]          # (k,)
        scores   = self._item_factors @ user_vec         # (n_items,)

        # Suppress items the user has already interacted with
        already_seen = self._matrix[user_idx] > 0
        scores = scores.copy()
        scores[already_seen] = -np.inf

        # Descending sort; collect up to top_n non-masked items
        sorted_idx = np.argsort(scores)[::-1]
        result: list[int] = []
        for i in sorted_idx:
            if len(result) >= top_n:
                break
            if scores[i] > -np.inf:
                result.append(self._item_ids[i])

        return result

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def save(self, path: str) -> None:
        joblib.dump(self, path)

    @classmethod
    def load(cls, path: str) -> CollaborativeFilteringTrainer:
        return joblib.load(path)
