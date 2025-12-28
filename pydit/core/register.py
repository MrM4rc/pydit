import inspect
from typing import Any, cast, overload
from pydit.core.dependencies import Dependency, dependencies, subclasses_map
from pydit.utils.get_class_token import get_class_token


@overload
def injectable(value: type[Any], *, token: str | None = None) -> None:
    pass


@overload
def injectable(value: Any, *, token: str) -> None:
    pass


def injectable(value: Any | type[Any], *, token: str | None = None) -> None:
    is_klass = inspect.isclass(value)

    token_ = cast(str, get_class_token(value) if is_klass and token is None else token)

    dependency = Dependency(value=value, token=token_)

    dependencies[token_] = dependency

    if not is_klass and type(value).__module__ == "builtins":
        return

    if not is_klass:
        klass = value.__class__
    else:
        klass = value

    for base in klass.__mro__:
        if base is object:
            continue

        subclasses_map.setdefault(base, []).append(dependency)
