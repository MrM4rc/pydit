from typing import Any, Callable

from pydit.core.dependencies import Dependency, EmptyDependency


def FunctionInject(
    type_: type[Any] | Callable[..., Any] | None = None,
    token: str | None = None,
    *,
    singleton: bool = False,
) -> Any:
    if not type_ and not token:
        return EmptyDependency(singleton=singleton)

    return Dependency(value=type_, token=token or "", singleton=singleton)
