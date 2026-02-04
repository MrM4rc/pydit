from fastapi import APIRouter
from src.configs.di import pydit
from src.domain.user.models.user import UserModel
from src.domain.user.module import UserModule
from src.mappers.user import UserMapper
from src.schemas.user.create_user import CreateUserSchema


user_module = UserModule()
user_router = APIRouter(prefix="/users")
user_mapper = UserMapper()


@user_router.post("")
def create(data: CreateUserSchema) -> None:
    user_module.create(user_mapper.ceate_to_domain_create(data))

@user_router.post("/create-by-fn")
async def create_by_fn(data: CreateUserSchema) -> None:
    create_user_fn = pydit.get_value(token="create_user_fn")

    create_user_fn(user_mapper.ceate_to_domain_create(data))

@user_router.get("")
def list_() -> list[UserModel]:
    return user_module.list_()

@user_router.get("/list-by-fn")
def list_by_fn() -> list[UserModel]:
    list_fn = pydit.get_value(token="list_user_fn")

    return list_fn()
