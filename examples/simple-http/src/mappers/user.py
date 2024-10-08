from src.domain.user.models.create_user import CreateUserModel
from src.schemas.user.create_user import CreateUserSchema


class UserMapper:
    def ceate_to_domain_create(self, data: CreateUserSchema) -> CreateUserModel:
        return CreateUserModel(
            id=data.id, name=data.name, last_name=data.lastName, email=data.email
        )
