from time import sleep
from typing import TypedDict, override
from uuid import UUID
from src.configs.di import pydit
from src.adapters.repositories.interfaces.user import UserRepository
from src.constants.injection import MEMORY_REPOSITORY_CONFIG_TOKEN
from src.domain.user.models.user import UserModel


class ConfigType(TypedDict):
    delay: int


class MemoryUserRepository(UserRepository):

    __users: dict[UUID, UserModel] = {}

    def __init__(self):
        self.__delay = self.config.get("delay", 0.2)

    @pydit.inject(token=MEMORY_REPOSITORY_CONFIG_TOKEN)
    def config(self) -> ConfigType:  # TODO: supress return type error
        pass

    @override
    def get_by_id(self, *, id_: UUID) -> UserModel:
        sleep(self.__delay)

        user = self.__users.get(id_)

        if user is None:
            raise ValueError("User not found")

        return user

    @override
    def save(self, *, data: UserModel) -> None:
        sleep(self.__delay)
        self._check_pk_conflict(pk=data.id)

        self.__users[data.id] = data

    @override
    def list_(self) -> list[UserModel]:
        return list(self.__users.values())

    def _check_pk_conflict(self, *, pk: UUID) -> None:
        if pk not in self.__users:
            return

        raise ValueError("Primary key conflicts: DB alrady has a user with this ID")
