from typing import Any, Callable, Protocol, TypeVar, cast, get_type_hints
from typing_extensions import override
from pydit.core.register import injectable
from pydit.core.resolver import DependencyResolver
from pydit.exceptions.missing_property_type import MissingPropertyTypeException
from pydit.types.dependency_property import DependencyPropertyType
from pydit.utils.logging import disable_all_loggers


R = TypeVar("R")


class GetInstanceFnType(Protocol[R]):
    def __call__(self, type_: type[R] | R, token: str | None = None, singleton: bool = False) -> R: ...


class PyDit:
    __singleton_instances: dict[Any, Any] = {}

    def __init__(self):
        self._dep_resolver = DependencyResolver()

    def disable_logging(self):
        disable_all_loggers()

    def add_dependency(self, value: Any, token: str | None = None):
        injectable(value, token=token)

    def inject(self, *, token: str | None = None, singleton: bool = False):
        def decorator(func: Callable[..., R]) -> DependencyPropertyType[R]:
            return self.DependencyProperty(
                func=func,
                token=token,
                dep_resolver=self._dep_resolver,
                get_value_fn=self._get_value,
                singleton=singleton,
            )

        return decorator

    class DependencyProperty(DependencyPropertyType[R]):
        _inject_type: R
        _token: str | None = None
        _dep_resolver: DependencyResolver
        _get_value_fn: GetInstanceFnType[R]
        _value: Any = None
        _singleton: bool = False

        def __init__(
            self,
            *,
            func: Callable[..., R],
            token: str | None = None,
            dep_resolver: DependencyResolver,
            get_value_fn: GetInstanceFnType[R],
            singleton: bool = False
        ):
            hints = get_type_hints(func)

            self._inject_type = cast(R, hints.get("return"))
            self._token = token
            self._dep_resolver = dep_resolver
            self._get_value_fn = get_value_fn
            self._singleton = singleton

            if self._inject_type is None:
                raise MissingPropertyTypeException

        @override
        def __get__(self, _instance: Any, _obj: Any = None) -> R:
            if self._value is not None:
                return self._value

            self._value = self._get_value_fn(type_=self._inject_type, token=self._token, singleton=self._singleton)

            return self._value

    def _get_value(self, type_: type[R] | R, token: str | None = None, singleton: bool = False) -> R:
        """
        This function will resolve __init__ signature in the future
        """
        dependency = self._dep_resolver.resolve_dependencies(type_, token)

        singleton_key = dependency.value if "__hash__" in dir(dependency.value) else dependency.token

        if singleton and singleton_key in self.__singleton_instances:
            return cast(R, self.__singleton_instances[singleton_key])

        is_callable = callable(dependency.value)

        response: R

        if not is_callable:
            response = cast(R, dependency.value)
        else:
            response = dependency.value()

        if singleton:
            self.__singleton_instances[singleton_key] = response

        return response
