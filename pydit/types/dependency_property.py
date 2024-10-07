from abc import abstractmethod
from typing import Any, Generic, Protocol, TypeVar

from pydit.exceptions.cant_set_dependency_property import (
    CantSetDependencyPropertyException,
)


T = TypeVar("T", covariant=True)


class DependencyPropertyType(Protocol, Generic[T]):
    @abstractmethod
    def __get__(self, instance: Any, obj: Any = None) -> T:
        raise NotImplementedError

    def __set__(self, instance: Any, value: Any) -> None:
        raise CantSetDependencyPropertyException
