from src.adapters.repositories.in_memory.user import MemoryUserRepository
from src.constants.injection import MEMORY_REPOSITORY_CONFIG_TOKEN
from .di import pydit
from .get_db_config import get_db_config


def setup_dependencies():
    pydit.add_dependency(get_db_config, token=MEMORY_REPOSITORY_CONFIG_TOKEN)
    pydit.add_dependency(MemoryUserRepository, "UserRepository")
