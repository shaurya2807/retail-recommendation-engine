from __future__ import annotations

import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ContentBasedRecommender:
    """TF-IDF content-based recommender over product text features."""

    def __init__(self, max_features: int = 500) -> None:
        self.max_features = max_features
        self._vectorizer: TfidfVectorizer | None = None
        self._tfidf_matrix = None                        # sparse (n_products, n_features)
        self._product_ids: list[int] = []                # row index → product_id
        self._product_index: dict[int, int] = {}         # product_id → row index

    # ------------------------------------------------------------------
    # Fitting
    # ------------------------------------------------------------------

    @staticmethod
    def _to_document(p: dict) -> str:
        parts = [
            p.get("name", ""),
            p.get("category", ""),
            p.get("subcategory") or "",
            p.get("description") or "",
        ]
        return " ".join(part for part in parts if part)

    def fit(self, products: list[dict]) -> ContentBasedRecommender:
        """Build TF-IDF matrix from product text fields.

        Args:
            products: List of dicts with at minimum keys: id, name,
                      category, subcategory, description.
        """
        self._product_ids   = [int(p["id"]) for p in products]
        self._product_index = {pid: i for i, pid in enumerate(self._product_ids)}

        corpus = [self._to_document(p) for p in products]
        self._vectorizer   = TfidfVectorizer(max_features=self.max_features)
        self._tfidf_matrix = self._vectorizer.fit_transform(corpus)
        return self

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def predict(self, product_id: int, top_n: int = 10) -> list[int]:
        """Return top_n product IDs most similar to product_id (excluding itself)."""
        if self._tfidf_matrix is None:
            raise RuntimeError("Not fitted. Call fit() first.")

        idx = self._product_index.get(product_id)
        if idx is None:
            return []

        sims = cosine_similarity(self._tfidf_matrix[idx], self._tfidf_matrix).flatten()
        sims[idx] = -np.inf  # exclude query product

        top_indices = np.argsort(sims)[::-1]
        return [
            self._product_ids[i]
            for i in top_indices
            if not np.isneginf(sims[i])
        ][:top_n]

    def predict_for_user(
        self,
        user_interacted_product_ids: list[int],
        top_n: int = 10,
    ) -> list[int]:
        """Return top_n unseen products by proximity to the user's averaged TF-IDF profile."""
        if self._tfidf_matrix is None:
            raise RuntimeError("Not fitted. Call fit() first.")

        valid_idx = [
            self._product_index[pid]
            for pid in user_interacted_product_ids
            if pid in self._product_index
        ]
        if not valid_idx:
            return []

        user_profile = np.asarray(self._tfidf_matrix[valid_idx].mean(axis=0))
        sims = cosine_similarity(user_profile, self._tfidf_matrix).flatten()

        seen = set(valid_idx)
        result: list[int] = []
        for i in np.argsort(sims)[::-1]:
            if len(result) >= top_n:
                break
            if i not in seen:
                result.append(self._product_ids[i])
        return result

    def score_all_for_user(self, user_interacted_product_ids: list[int]) -> dict[int, float]:
        """Return cosine-similarity score for every product given the user's history.

        Used by HybridRecommender to obtain a dense score vector before blending.
        """
        if self._tfidf_matrix is None:
            raise RuntimeError("Not fitted. Call fit() first.")

        valid_idx = [
            self._product_index[pid]
            for pid in user_interacted_product_ids
            if pid in self._product_index
        ]
        if not valid_idx:
            return {pid: 0.0 for pid in self._product_ids}

        user_profile = np.asarray(self._tfidf_matrix[valid_idx].mean(axis=0))
        sims = cosine_similarity(user_profile, self._tfidf_matrix).flatten()
        return {self._product_ids[i]: float(sims[i]) for i in range(len(self._product_ids))}

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def save(self, path: str) -> None:
        joblib.dump(self, path)

    @classmethod
    def load(cls, path: str) -> ContentBasedRecommender:
        return joblib.load(path)
