from typing import cast
from src.configs.di import pydit
from src.adapters.repositories.interfaces.user import UserRepository
from src.domain.user.models.user import UserModel


class ListUsersService:
    @pydit.inject()
    def user_repository(self) -> UserRepository:
        return cast(UserRepository, None)

    def execute(self) -> list[UserModel]:
        return self.user_repository.list_()
