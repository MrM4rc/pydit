from typing import Any


class DependencyProxy:
    def __init__(self, value: Any):
        self._pydit_value = value

    def __getattribute__(self, item: str):
        if item in ["_get_real_dependency", "_pydit_value", "__is_proxy__"]:
            return super().__getattribute__(item)

        real_dependency = self._get_real_dependency()

        return getattr(real_dependency, item)

    def __setattr__(self, key: str, value: Any):
        if key in ["_get_real_dependency", "_pydit_value", "__is_proxy__"]:
            super().__setattr__(key, value)
        else:
            real_dependency = self._get_real_dependency()
            setattr(real_dependency, key, value)

    def __delattr__(self, item: str):
        if item in ["_get_real_dependency", "_pydit_value", "__is_proxy__"]:
            super().__delattr__(item)
        else:
            real_dependency = self._get_real_dependency()
            delattr(real_dependency, item)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DependencyProxy):
            return self._get_real_dependency() == other._get_real_dependency()

        return self._get_real_dependency() == other

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self._get_real_dependency())

    def __len__(self) -> int:
        return len(self._get_real_dependency())

    def __iter__(self):
        return iter(self._get_real_dependency())

    def __getitem__(self, item: Any) -> Any:
        return self._get_real_dependency()[item]

    def __contains__(self, item: Any) -> bool:
        return item in self._get_real_dependency()

    def __bool__(self) -> bool:
        return bool(self._get_real_dependency())

    def __reduce__(self):
        real_reduce = getattr(self._get_real_dependency(), "__reduce__", None)
        if real_reduce:
            return real_reduce()

        return self._get_real_dependency()
    
    def __repr__(self) -> str:
        return repr(self._get_real_dependency())

    def __sizeof__(self) -> int:
        return self._get_real_dependency().__sizeof__()

    def __format__(self, format_spec: str) -> str:
        return self._get_real_dependency().__format__(format_spec)

    def __str__(self) -> str:
        return str(self._get_real_dependency())

    def _get_real_dependency(self) -> Any:
        value = super().__getattribute__("_pydit_value")

        if callable(value):
            return value()

        return value

    def __is_proxy__(self) -> bool:
        return True


def create_proxy_method(method_name: str) -> Any:
    def proxy_method(self: DependencyProxy, *args: Any, **kwargs: Any) -> Any:
        real_dependency = self._get_real_dependency()
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
    if hasattr(DependencyProxy, dunder):
        continue

    setattr(
        DependencyProxy,
        dunder,
        create_proxy_method(dunder),
    )
