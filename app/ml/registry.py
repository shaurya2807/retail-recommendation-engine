from __future__ import annotations

import pickle
from pathlib import Path

from app.ml.trainer import CollaborativeFilteringTrainer
from app.repository.model_registry_repo import ModelRegistryRepository


class ModelRegistry:
    def __init__(
        self,
        repo: ModelRegistryRepository,
        model_dir: str = "models",
    ) -> None:
        self._repo = repo
        self._model_dir = Path(model_dir)
        self._model_dir.mkdir(parents=True, exist_ok=True)

    def save_and_register(
        self,
        trainer: CollaborativeFilteringTrainer,
        model_name: str,
        version: str,
        metrics: dict,
    ) -> None:
        raise NotImplementedError

    def load_active(self, model_name: str) -> CollaborativeFilteringTrainer | None:
        raise NotImplementedError
