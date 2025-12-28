from typing import Any, cast

from pydit.core.dependencies import Dependency, EmptyDependency


def ConstructorInject(type_: type[Any] | None = None, token: str | None = None) -> Any:
    if not type_ and not token:
        return EmptyDependency()

    if not token and type_:
        token = type_.__name__

    return Dependency(value=type_, token=cast(str, token))
