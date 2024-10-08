from abc import abstractmethod
from typing import Protocol
from uuid import UUID
from src.domain.user.models.user import UserModel


class UserRepository(Protocol):
    @abstractmethod
    def get_by_id(self, *, id_: UUID) -> UserModel:
        pass

    @abstractmethod
    def save(self, *, data: UserModel) -> None:
        pass

    @abstractmethod
    def list_(self) -> list[UserModel]:
        pass
