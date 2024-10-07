import inspect
from typing import Any, cast, overload
from pydit.core.dependencies import Dependency, dependencies


@overload
def injectable(value: type[Any], *, token: str | None = None) -> None:
    pass


@overload
def injectable(value: Any, *, token: str) -> None:
    pass


def injectable(value: Any | type[Any], *, token: str | None = None) -> None:
    is_klass = inspect.isclass(value)

    token_ = cast(str, value.__name__ if is_klass and token is None else token)

    dependencies[token_] = Dependency(value=value, token=token_)
