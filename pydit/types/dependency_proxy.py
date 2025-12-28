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


for dunder in dir(object):
    if dunder in (
        "__class__",
        "__dict__",
        "__weakref__",
        "__init__",
        "__new__",
        "__getattribute__",
        "__setattr__",
        "__delattr__",
    ):
        continue

    if dunder.startswith("__") and dunder.endswith("__"):
        setattr(
            DependencyProxy,
            dunder,
            create_proxy_method(dunder),
        )
