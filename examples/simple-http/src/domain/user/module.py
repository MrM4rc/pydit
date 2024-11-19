from typing import cast
from src.adapters.repositories.interfaces.user import UserRepository
from src.configs.di import pydit
from src.domain.user.models.create_user import CreateUserModel
from src.domain.user.models.user import UserModel
from src.domain.user.services.create import CreateUserService
from src.domain.user.services.list import ListUsersService


class UserModule:
    @pydit.inject()
    def user_repository(self) -> UserRepository:
        return cast(UserRepository, None)

    def create(self, data: CreateUserModel) -> None:
        CreateUserService(self.user_repository).execute(data)

    def list_(self) -> list[UserModel]:
        return ListUsersService().execute()
