from app.models.user import User, UserCreate
from app.repository.db import db_cursor


class UserRepository:
    def get_all(self) -> list[User]:
        with db_cursor() as cur:
            cur.execute("SELECT id, username, created_at FROM users ORDER BY id")
            return [User(**dict(row)) for row in cur.fetchall()]

    def get_by_id(self, user_id: int) -> User | None:
        with db_cursor() as cur:
            cur.execute(
                "SELECT id, username, created_at FROM users WHERE id = %s",
                (user_id,),
            )
            row = cur.fetchone()
        return User(**dict(row)) if row else None

    def get_by_username(self, username: str) -> User | None:
        with db_cursor() as cur:
            cur.execute(
                "SELECT id, username, created_at FROM users WHERE username = %s",
                (username,),
            )
            row = cur.fetchone()
        return User(**dict(row)) if row else None

    def create(self, user: UserCreate) -> User:
        raise NotImplementedError
