from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

InteractionType = Literal["view", "cart", "purchase"]


class InteractionBase(BaseModel):
    user_id: int
    product_id: int
    interaction_type: InteractionType
    rating: int | None = Field(None, ge=1, le=5)


class InteractionCreate(InteractionBase):
    pass


class Interaction(InteractionBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
