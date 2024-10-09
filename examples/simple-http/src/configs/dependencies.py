from src.adapters.repositories.in_memory.user import MemoryUserRepository
from src.constants.injection import MEMORY_REPOSITORY_CONFIG_TOKEN
from .di import pydit


def setup_dependencies():
    pydit.add_dependency({"delay": 0.5}, token=MEMORY_REPOSITORY_CONFIG_TOKEN)
    pydit.add_dependency(MemoryUserRepository, "UserRepository")
