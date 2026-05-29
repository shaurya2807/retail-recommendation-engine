from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
