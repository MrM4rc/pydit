from src.adapters.repositories.interfaces.user import UserRepository
from src.configs.di import pydit
from src.domain.user.models.create_user import CreateUserModel
from src.domain.user.services.create import CreateUserService


class UserModule:
    @pydit.inject()
    def user_repository(self) -> UserRepository:
        pass

    def create(self, data: CreateUserModel) -> None:
        CreateUserService(
                self.user_repository
        ).execute(data)
