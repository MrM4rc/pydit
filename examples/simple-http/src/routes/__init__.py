from fastapi import APIRouter
from .hello import hello_router
from .user import user_router


app_router = APIRouter()

app_router.include_router(hello_router)
app_router.include_router(user_router)
