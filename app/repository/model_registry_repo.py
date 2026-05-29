from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ModelRecord:
    id: int
    model_name: str
    version: str
    metrics: dict
    model_path: str
    created_at: datetime
    is_active: bool


class ModelRegistryRepository:
    def register(
        self,
        model_name: str,
        version: str,
        metrics: dict,
        model_path: str,
    ) -> ModelRecord:
        raise NotImplementedError

    def get_active(self, model_name: str) -> ModelRecord | None:
        raise NotImplementedError

    def activate(self, model_name: str, version: str) -> None:
        raise NotImplementedError
