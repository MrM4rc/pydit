from dataclasses import dataclass
from typing import Any
from pydit.types.dependency import Dependency as DependencyType


@dataclass
class Dependency:
    value: Any
    token: str


dependencies: dict[str, DependencyType] = {}

subclasses_map: dict[type[Any], list[DependencyType]] = {}
