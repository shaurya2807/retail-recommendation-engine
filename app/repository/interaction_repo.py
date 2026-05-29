from app.models.interaction import Interaction, InteractionCreate


class InteractionRepository:
    def create(self, interaction: InteractionCreate) -> Interaction:
        raise NotImplementedError

    def get_by_user(self, user_id: int) -> list[Interaction]:
        raise NotImplementedError

    def get_all(self) -> list[Interaction]:
        raise NotImplementedError
