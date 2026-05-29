import pandas as pd

from app.models.interaction import Interaction, InteractionCreate
from app.repository.db import db_cursor

_WEIGHTS: dict[str, int] = {"view": 1, "cart": 2, "purchase": 3}


class InteractionRepository:
    def get_all(self) -> list[Interaction]:
        with db_cursor() as cur:
            cur.execute(
                "SELECT id, user_id, product_id, interaction_type, rating, created_at"
                " FROM interactions ORDER BY created_at"
            )
            return [Interaction(**dict(row)) for row in cur.fetchall()]

    def get_by_user_id(self, user_id: int) -> list[Interaction]:
        with db_cursor() as cur:
            cur.execute(
                "SELECT id, user_id, product_id, interaction_type, rating, created_at"
                " FROM interactions WHERE user_id = %s ORDER BY created_at",
                (user_id,),
            )
            return [Interaction(**dict(row)) for row in cur.fetchall()]

    def get_interaction_matrix(self) -> pd.DataFrame:
        """Return a user × product pivot of max interaction values.

        Value per row: explicit rating (1-5) if present, else interaction weight
        (purchase=3, cart=2, view=1). Each (user, product) cell holds the maximum
        value across all recorded interactions.
        """
        with db_cursor() as cur:
            cur.execute(
                "SELECT user_id, product_id, interaction_type, rating FROM interactions"
            )
            rows = cur.fetchall()

        if not rows:
            return pd.DataFrame()

        records = [
            {
                "user_id": row["user_id"],
                "product_id": row["product_id"],
                "value": (
                    row["rating"]
                    if row["rating"] is not None
                    else _WEIGHTS[row["interaction_type"]]
                ),
            }
            for row in rows
        ]

        df = pd.DataFrame(records)
        agg = df.groupby(["user_id", "product_id"])["value"].max().reset_index()
        matrix = agg.pivot(index="user_id", columns="product_id", values="value").fillna(0)
        matrix.columns.name = None
        matrix.index.name = None
        return matrix

    def create(self, interaction: InteractionCreate) -> Interaction:
        raise NotImplementedError
