from dataclasses import dataclass
from typing import Any, Callable
from pydit.types.dependency import IDependency


@dataclass
class Dependency:
    value: Any
    token: str


class EmptyDependency:
    pass


dependencies: dict[str, IDependency] = {}

subclasses_map: dict[type[Any] | Callable[..., Any], list[IDependency]] = {}
