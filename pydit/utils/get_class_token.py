import inspect
from typing import Any


def get_class_token(type_: type[Any]) -> str:

    return f"{inspect.getfile(type_)} - {type_.__name__}"
