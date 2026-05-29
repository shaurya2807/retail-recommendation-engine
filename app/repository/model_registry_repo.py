from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime

from app.repository.db import db_cursor


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
    def save_model(
        self,
        model_name: str,
        version: str,
        metrics: dict,
        model_path: str,
    ) -> ModelRecord:
        with db_cursor() as cur:
            cur.execute(
                """
                INSERT INTO model_registry (model_name, version, metrics, model_path)
                VALUES (%s, %s, %s::jsonb, %s)
                ON CONFLICT (model_name, version) DO UPDATE
                    SET metrics    = EXCLUDED.metrics,
                        model_path = EXCLUDED.model_path,
                        is_active  = FALSE
                RETURNING id, model_name, version, metrics, model_path, created_at, is_active
                """,
                (model_name, version, json.dumps(metrics), model_path),
            )
            row = cur.fetchone()
        return ModelRecord(**dict(row))

    def get_active_model(self, model_name: str) -> ModelRecord | None:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT id, model_name, version, metrics, model_path, created_at, is_active
                FROM model_registry
                WHERE model_name = %s AND is_active = TRUE
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (model_name,),
            )
            row = cur.fetchone()
        return ModelRecord(**dict(row)) if row else None

    def list_versions(self, model_name: str) -> list[ModelRecord]:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT id, model_name, version, metrics, model_path, created_at, is_active
                FROM model_registry
                WHERE model_name = %s
                ORDER BY created_at DESC
                """,
                (model_name,),
            )
            rows = cur.fetchall()
        return [ModelRecord(**dict(row)) for row in rows]

    def set_active(self, model_id: int) -> None:
        with db_cursor() as cur:
            cur.execute(
                "SELECT model_name FROM model_registry WHERE id = %s",
                (model_id,),
            )
            row = cur.fetchone()
            if row is None:
                raise ValueError(f"No model found with id={model_id}")
            model_name = row["model_name"]

            # Deactivate all versions, then activate the target.
            cur.execute(
                "UPDATE model_registry SET is_active = FALSE WHERE model_name = %s",
                (model_name,),
            )
            cur.execute(
                "UPDATE model_registry SET is_active = TRUE WHERE id = %s",
                (model_id,),
            )
