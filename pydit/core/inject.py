from typing import Any, Callable

from pydit.core.dependencies import Dependency, EmptyDependency


def FunctionInject(type_: type[Any] | Callable[..., Any] | None = None, token: str | None = None) -> Any:
    if not type_ and not token:
        return EmptyDependency()

    return Dependency(value=type_, token=token or "")
