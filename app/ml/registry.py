from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib

from app.repository.model_registry_repo import ModelRecord, ModelRegistryRepository


class ModelRegistry:
    """Bridges the ML trainer with the model_registry database table."""

    def __init__(
        self,
        repo: ModelRegistryRepository,
        model_dir: str = "models",
    ) -> None:
        self._repo = repo
        self._model_dir = Path(model_dir)
        self._model_dir.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        trainer: Any,
        model_name: str,
        version: str,
        metrics: dict,
    ) -> ModelRecord:
        """Serialise trainer to disk, upsert the DB record, and mark active."""
        filename   = f"{model_name}_v{version}.joblib"
        model_path = str(self._model_dir / filename)

        trainer.save(model_path)
        record = self._repo.save_model(model_name, version, metrics, model_path)
        self._repo.set_active(record.id)
        record.is_active = True  # reflect the DB update in the returned object
        return record

    def load_active(self, model_name: str) -> Any:
        """Load the active model from disk; returns None if none is registered."""
        record = self._repo.get_active_model(model_name)
        if record is None:
            return None
        return joblib.load(record.model_path)

    def list_versions(self, model_name: str) -> list[ModelRecord]:
        """Return all registered versions for a model, newest first."""
        return self._repo.list_versions(model_name)
