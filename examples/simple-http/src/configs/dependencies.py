from src.adapters.repositories.in_memory.user import MemoryUserRepository
from src.constants.injection import MEMORY_REPOSITORY_CONFIG_TOKEN
from .di import pydit
from .get_db_config import get_db_config
from src.domain.user.services.list import list_fn
from src.domain.user.services.create import create_user_fn


def setup_dependencies():
    pydit.add_dependency(get_db_config, token=MEMORY_REPOSITORY_CONFIG_TOKEN)
    pydit.add_dependency(MemoryUserRepository, "UserRepository")
    pydit.add_dependency(list_fn, "list_user_fn")
    pydit.add_dependency(create_user_fn, "create_user_fn")

