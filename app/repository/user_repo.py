from app.models.user import User, UserCreate


class UserRepository:
    def get_by_id(self, user_id: int) -> User | None:
        raise NotImplementedError

    def get_by_username(self, username: str) -> User | None:
        raise NotImplementedError

    def create(self, user: UserCreate) -> User:
        raise NotImplementedError
