from .configs.dependencies import setup_dependencies
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

setup_dependencies()


def register_router(app: FastAPI):
    from .routes import app_router

    app.include_router(app_router)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_router(app)
