from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD


class CollaborativeFilteringTrainer:
    """SVD-based collaborative filtering on a user-item interaction matrix."""

    def __init__(self, n_components: int = 50, random_state: int = 42) -> None:
        self.n_components = n_components
        self.random_state = random_state
        self._svd: TruncatedSVD | None = None
        self._user_factors: np.ndarray | None = None
        self._item_factors: np.ndarray | None = None
        self._user_index: dict[int, int] = {}
        self._item_index: dict[int, int] = {}

    def fit(self, interactions: pd.DataFrame) -> None:
        """Build and decompose the user-item matrix.

        Args:
            interactions: DataFrame with columns [user_id, product_id, score].
        """
        raise NotImplementedError

    def predict(self, user_id: int, top_k: int = 10) -> list[tuple[int, float]]:
        """Return (product_id, score) pairs ranked by predicted affinity."""
        raise NotImplementedError
