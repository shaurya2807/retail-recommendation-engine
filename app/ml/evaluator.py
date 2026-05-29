from __future__ import annotations

import numpy as np
import pandas as pd


class RecommendationEvaluator:
    """Computes standard ranking metrics for offline evaluation."""

    @staticmethod
    def precision_at_k(relevant: set[int], recommended: list[int], k: int) -> float:
        raise NotImplementedError

    @staticmethod
    def recall_at_k(relevant: set[int], recommended: list[int], k: int) -> float:
        raise NotImplementedError

    @staticmethod
    def ndcg_at_k(relevant: set[int], recommended: list[int], k: int) -> float:
        raise NotImplementedError

    def evaluate(
        self,
        test_interactions: pd.DataFrame,
        predictions: dict[int, list[int]],
        k: int = 10,
    ) -> dict[str, float]:
        """Aggregate precision, recall, and nDCG across all users."""
        raise NotImplementedError
