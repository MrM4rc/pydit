from typing import cast
from typing import TypeVar
from typing import Any


T = TypeVar("T")


def DependencyProxy(value: T) -> T:
    return cast(T, _DependencyProxy(value))


class _DependencyProxy:
    def __init__(self, value: Any) -> None:
        self._pydit_value = value

    @property  # type: ignore[misc]
    def __class__(self) -> type:  # pyrefly: ignore[bad-override]
        return self.unwrap().__class__

    def __getattr__(self, name: str) -> Any:
        if name in ["_get_real_dependency", "_pydit_value", "__is_proxy__", "unwrap"]:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )
        else:
            real_dependency = self.unwrap()
            return getattr(real_dependency, name)

    def __setattr__(self, key: str, value: Any) -> None:
        if key in ["_get_real_dependency", "_pydit_value", "__is_proxy__", "unwrap"]:
            super().__setattr__(key, value)
        else:
            real_dependency = self.unwrap()
            setattr(real_dependency, key, value)

    def __delattr__(self, item: str) -> None:
        if item in ["_get_real_dependency", "_pydit_value", "__is_proxy__"]:
            super().__delattr__(item)
        else:
            real_dependency = self.unwrap()
            delattr(real_dependency, item)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _DependencyProxy):
            return bool(self.unwrap() == other.unwrap())

        return bool(self.unwrap() == other)

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.unwrap())

    def __len__(self) -> int:
        return len(self.unwrap())

    def __iter__(self) -> Any:
        return iter(self.unwrap())

    def __getitem__(self, item: Any) -> Any:
        return self.unwrap()[item]

    def __contains__(self, item: Any) -> bool:
        return item in self.unwrap()

    def __bool__(self) -> bool:
        return bool(self.unwrap())

    def __reduce__(self) -> Any:
        real_reduce = getattr(self.unwrap(), "__reduce__", None)
        if real_reduce:
            return real_reduce()

        return self.unwrap()

    def __repr__(self) -> str:
        return repr(self.unwrap())

    def __sizeof__(self) -> int:
        return int(self.unwrap().__sizeof__())

    def __format__(self, format_spec: str) -> str:
        return str(self.unwrap().__format__(format_spec))

    def __str__(self) -> str:
        return str(self.unwrap())

    def __is_proxy__(self) -> bool:
        return True

    def unwrap(self) -> Any:
        return self._pydit_value


def create_proxy_method(method_name: str) -> Any:
    def proxy_method(self: _DependencyProxy, *args: Any, **kwargs: Any) -> Any:
        real_dependency = self.unwrap()
        method = getattr(real_dependency, method_name)
        return method(*args, **kwargs)

    return proxy_method


_special_names = [
    "__abs__",
    "__add__",
    "__and__",
    "__call__",
    "__cmp__",
    "__coerce__",
    "__contains__",
    "__delitem__",
    "__delslice__",
    "__div__",
    "__divmod__",
    "__eq__",
    "__float__",
    "__floordiv__",
    "__ge__",
    "__getitem__",
    "__getslice__",
    "__gt__",
    "__hash__",
    "__hex__",
    "__iadd__",
    "__iand__",
    "__idiv__",
    "__idivmod__",
    "__ifloordiv__",
    "__ilshift__",
    "__imod__",
    "__imul__",
    "__int__",
    "__invert__",
    "__ior__",
    "__ipow__",
    "__irshift__",
    "__isub__",
    "__iter__",
    "__itruediv__",
    "__ixor__",
    "__le__",
    "__len__",
    "__long__",
    "__lshift__",
    "__lt__",
    "__mod__",
    "__mul__",
    "__ne__",
    "__neg__",
    "__oct__",
    "__or__",
    "__pos__",
    "__pow__",
    "__radd__",
    "__rand__",
    "__rdiv__",
    "__rdivmod__",
    "__reduce__",
    "__reduce_ex__",
    "__repr__",
    "__reversed__",
    "__rfloordiv__",
    "__rlshift__",
    "__rmod__",
    "__rmul__",
    "__ror__",
    "__rpow__",
    "__rrshift__",
    "__rsub__",
    "__rtruediv__",
    "__rxor__",
    "__setitem__",
    "__setslice__",
    "__sub__",
    "__truediv__",
    "__xor__",
    "__next__",
    "__bool__",
]

for dunder in _special_names:
    if hasattr(_DependencyProxy, dunder):
        continue

    setattr(
        _DependencyProxy,
        dunder,
        create_proxy_method(dunder),
    )
