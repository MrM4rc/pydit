from dataclasses import KW_ONLY
from dataclasses import InitVar
from dataclasses import field
from dataclasses import dataclass
from typing import Any, Callable
from pydit.types.dependency import IDependency


@dataclass
class EmptyDependency:
    _: KW_ONLY
    singleton: InitVar[bool] = False
    __pydit_meta__: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self, singleton: bool = False) -> None:
        self.__pydit_meta__["singleton"] = singleton


@dataclass
class Dependency:
    value: Any
    token: str

    _: KW_ONLY
    singleton: InitVar[bool] = False
    __pydit_meta__: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self, singleton: bool = False) -> None:
        self.__pydit_meta__["singleton"] = singleton


dependencies: dict[str, IDependency] = {}

subclasses_map: dict[type[Any] | Callable[..., Any], list[IDependency]] = {}
