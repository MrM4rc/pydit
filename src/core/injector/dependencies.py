from dataclasses import dataclass
from typing import Any
from src.core.types.dependency import Dependency as DependencyType


@dataclass
class Dependency:
    value: Any
    token: str


dependencies: dict[str, DependencyType] = {}
