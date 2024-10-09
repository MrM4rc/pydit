from src.adapters.repositories.interfaces.user import UserRepository
from src.domain.user.models.create_user import CreateUserModel
from src.domain.user.models.user import UserModel


class CreateUserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(self, data: CreateUserModel):
        user = UserModel(
            id=data.id,
            name=data.name,
            last_name=data.last_name,
            email=data.email,
        )

        self.repository.save(data=user)
