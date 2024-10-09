from fastapi import APIRouter

hello_router = APIRouter(prefix="/hello")


@hello_router.get("/world")
def world():
    return "Hello, World"
