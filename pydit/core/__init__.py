from typing import overload
import functools
import inspect
from typing import Any, Callable, Protocol, TypeVar, cast, get_type_hints
from typing_extensions import override
from pydit.core.register import injectable
from pydit.core.resolver import DependencyMapping, DependencyResolver
from pydit.exceptions.missing_property_type import MissingPropertyTypeException
from pydit.types.dependency_property import DependencyPropertyType
from pydit.types.dependency_proxy import _DependencyProxy as DependencyProxy
from pydit.utils.logging import disable_all_loggers


R = TypeVar("R")


class GetInstanceFnType(Protocol[R]):
    @overload
    def __call__(  # type: ignore[overload-overlap] # pyright: ignore[reportOverlappingOverload]
        self,
        type_: type[R],
        token: str | None = None,
        singleton: bool = False,
    ) -> R: ...

    @overload
    def __call__(
        self,
        type_: Callable[..., R],
        token: str | None = None,
        singleton: bool = False,
    ) -> Callable[..., R]: ...

    def __call__(
        self,
        type_: type[R] | Callable[..., R] | None = None,
        token: str | None = None,
        singleton: bool = False,
    ) -> R | Callable[..., R]: ...


InjectType = Callable[[Callable[..., R]], R]


class PyDit:
    __singleton_instances: dict[Any, Any] = {}

    def __init__(self) -> None:
        self._dep_resolver = DependencyResolver()

    def disable_logging(self):
        disable_all_loggers()

    def add_dependency(self, value: Any, token: str | None = None) -> None:
        injectable(value, token=token)

    def inject(
        self, *, token: str | None = None, singleton: bool = False
    ) -> Callable[[Callable[..., R]], DependencyPropertyType[R]]:
        def decorator(func: Callable[..., R]) -> DependencyPropertyType[R]:
            return self.DependencyProperty(
                func=func,
                token=token,
                get_value_fn=self.get_value,
                singleton=singleton,
            )

        return decorator

    class DependencyProperty(DependencyPropertyType[R]):
        _inject_type: type[R] | Callable[..., Any]
        _token: str | None = None
        _get_value_fn: GetInstanceFnType[R]
        _value: Any = None
        _singleton: bool = False

        def __init__(
            self,
            *,
            func: Callable[..., R],
            token: str | None = None,
            get_value_fn: GetInstanceFnType[R],
            singleton: bool = False,
        ):
            hints = get_type_hints(func)

            self._inject_type = cast(type[R], hints.get("return"))
            self._token = token
            self._get_value_fn = get_value_fn
            self._singleton = singleton

            if self._inject_type is None:
                raise MissingPropertyTypeException

        @override
        def __get__(self, instance: Any, obj: Any = None) -> R:
            if self._value is not None:
                return self._value

            self._value = self._get_value_fn(
                type_=self._inject_type, token=self._token, singleton=self._singleton
            )

            return cast(R, self._value)

    @overload
    def get_value(  # type: ignore[overload-overlap] # pyright: ignore[reportOverlappingOverload]
        self, type_: type[R], token: str | None = None, singleton: bool = False
    ) -> R: ...

    @overload
    def get_value(
        self, type_: Callable[..., R], token: str | None = None, singleton: bool = False
    ) -> Callable[..., R]: ...

    def get_value(
        self,
        type_: type[R] | Callable[..., R] | None = None,
        token: str | None = None,
        singleton: bool = False,
    ) -> R | Callable[..., R]:
        """
        This function will resolve __init__ signature in the future
        """
        resolver_response = self._dep_resolver.resolve(type_, token)

        dependency = resolver_response[0][0]

        singleton_key = (
            dependency.value
            if "__hash__" in dir(dependency.value)
            else dependency.token
        )

        if singleton and singleton_key in self.__singleton_instances:
            return cast(R, self.__singleton_instances[singleton_key])

        is_callable = callable(dependency.value)

        if not is_callable:
            return cast(R, dependency.value)

        response = self._instantiate_type(resolver_response)[0]

        if singleton:
            self.__singleton_instances[singleton_key] = response

        return response

    def _instantiate_type(
        self,
        resolver_response: DependencyMapping,
        solved_klasses: dict[type[Any] | Callable[..., Any], Any] | None = None,
    ) -> list[Any]:
        response: list[Any] = []

        def get_real_values_by_proxies(
            *args: Any, **kwargs: Any
        ) -> tuple[list[Any], dict[str, Any]]:
            new_args: list[Any] = []
            new_kwargs: dict[str, Any] = {}

            for arg in args:
                if hasattr(arg, "__is_proxy__"):
                    new_args.append(arg.unwrap())
                    continue
                new_args.append(arg)

            for key, value in kwargs.items():
                if hasattr(value, "__is_proxy__"):
                    new_kwargs[key] = value.unwrap()
                    continue
                new_kwargs[key] = value

            return new_args, new_kwargs

        def fn_injection(
            *args: Any, **kwargs: Any
        ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
            def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:

                @functools.wraps(fn)
                def wrapper(*other_args: Any, **other_kwargs: Any) -> Any:
                    new_args, new_kwargs = get_real_values_by_proxies(
                        *[*other_args, *args], **{**other_kwargs, **kwargs}
                    )

                    return fn(*new_args, **new_kwargs)

                @functools.wraps(fn)
                async def async_wrapper(*other_args: Any, **other_kwargs: Any) -> Any:
                    new_args, new_kwargs = get_real_values_by_proxies(
                        *[*other_args, *args], *{**other_kwargs, **kwargs}
                    )

                    return await fn(*new_args, **new_kwargs)

                return wrapper if not inspect.iscoroutinefunction(fn) else async_wrapper

            return decorator

        if solved_klasses is None:
            solved_klasses = {}

        for dependency, parameters, is_singleton in resolver_response:
            is_callable = callable(dependency.value)

            if not is_callable:
                response.append(dependency.value)
                continue

            proxies: list[DependencyProxy] = []

            if is_singleton and dependency.value in self.__singleton_instances:
                response.append(self.__singleton_instances[dependency.value])
                continue

            if dependency.value in solved_klasses:
                response.append(solved_klasses[dependency.value])
                continue

            for _ in parameters:
                proxies.append(DependencyProxy(None))

            if inspect.isclass(dependency.value):
                solved = dependency.value(*proxies)
            else:
                solved = fn_injection(*proxies)(dependency.value)

            response.append(solved)
            solved_klasses[dependency.value] = solved

            if is_singleton:
                self.__singleton_instances[dependency.value] = solved

            if len(parameters) > 0:
                solved_params = self._instantiate_type(parameters, solved_klasses)

                for proxy, real in zip(proxies, solved_params):
                    setattr(proxy, "_pydit_value", real)

        return response
