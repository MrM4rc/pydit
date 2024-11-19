from typing import Any
from time import sleep


def get_db_config() -> dict[str, Any]:

    # simulates getting secrests from an external service
    sleep(0.4)

    return {"delay": 0.5}
