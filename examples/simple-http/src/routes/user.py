from fastapi import APIRouter
from src.domain.user.module import UserModule
from src.mappers.user import UserMapper
from src.schemas.user.create_user import CreateUserSchema


user_module = UserModule()
user_router = APIRouter(prefix="/users")
user_mapper = UserMapper()


@user_router.post("")
def create(data: CreateUserSchema) -> None:
    user_module.create(user_mapper.ceate_to_domain_create(data))
