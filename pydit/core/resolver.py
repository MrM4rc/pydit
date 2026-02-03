import inspect
from time import time
from types import MappingProxyType, NoneType
from typing import Any, Callable, Literal, get_type_hints
from pydit.exceptions.dependency_not_found import PyDitDependencyNotFoundException
from pydit.exceptions.missing_default_value import MissingDefaultValueException
from pydit.types.dependency import IDependency
from pydit.core.dependencies import Dependency, EmptyDependency, dependencies, subclasses_map
from pydit.utils.is_dunder import is_dunder
from pydit.utils.logging import get_logger
from pydit.utils.remove_dunders import remove_dunders
from pydit.utils.remove_private_protected import remove_private_and_protected_items


DependencyMapping = list[tuple[IDependency, "DependencyMapping"]]


class DependencyResolver:
    def __init__(self):
        self.logger = get_logger("pydit.core.resolver")
        self._solved_types: dict[type[Any] | Callable[..., Any], DependencyMapping] | None = None

    def resolve(self, type_: Any, token: str | None = None) -> DependencyMapping:
        start = time()
        dependency: IDependency | None = None

        is_type_callable = callable(type_)

        if token:
            dependency = dependencies.get(token)

        elif is_type_callable:
            dependency = self._resolve_by_type(type_)

        if dependency is None:
            raise PyDitDependencyNotFoundException

        self.logger.debug(
            f"Resolved dependency '{dependency.token}' " f"in {round((time() - start) * 1000, 2)} ms"
        )

        dependency_mapping: DependencyMapping = []

        is_dependency_callable = callable(dependency.value)

        if is_dependency_callable:
            dependency_mapping = self._get_callable_dependencies(dependency)

        response: DependencyMapping = [(dependency, dependency_mapping)]

        return response

    def _resolve_by_type(
        self,
        type_: type[Any] | Callable[..., Any],
        *,
        check_dunders: bool = False,
        dunders_to_check: Literal["all"] | list[str] = "all",
    ) -> IDependency | None:
        response: IDependency | None = None

        if type_ in subclasses_map:
            response = subclasses_map[type_][0]
            self.logger.debug(f"Resolved dependency by subclass map {type_}: {response}")

            return response

        for dependency in dependencies.values():
            if self._check_compatibility_by_annotations(type_, dependency, check_dunders, dunders_to_check):
                response = dependency
                self.logger.debug(f"Resolved dependency by annotations compatibility {type_}: {response}")
                break

        return response

    def _get_callable_dependencies(
        self,
        dependency: IDependency,
    ) -> DependencyMapping:
        dependency_mapping: DependencyMapping = []
        initialized_solved_types = False

        is_callable = callable(dependency.value)

        if is_callable:
            if self._solved_types is None:
                self._solved_types = {}
                self._solved_types[dependency.value] = dependency_mapping
                initialized_solved_types = True

            elif dependency.value in self._solved_types and not initialized_solved_types:
                return self._solved_types[dependency.value]

            dependency_mapping.extend(self._resolve_signature(dependency.value))
            self._solved_types[dependency.value] = dependency_mapping

        return dependency_mapping

    def _check_compatibility_by_annotations(
        self,
        type_: type[Any] | Callable[..., Any],
        dependency: IDependency,
        check_dunders: bool = False,
        dunders_to_check: Literal["all"] | list[str] = "all",
    ) -> bool:
        is_callable = callable(dependency.value)
        dep_klass = dependency.value if is_callable else dependency.value.__class__
        is_compatible = True

        type_properties = self._get_properties(type_, check_dunders, dunders_to_check)

        type_attributes = remove_private_and_protected_items(get_type_hints(type_), type_)
        dep_attributes = remove_private_and_protected_items(get_type_hints(dep_klass), dep_klass)

        if type_attributes != dep_attributes:
            return False

        verified = type_attributes.keys()

        type_properties = [property_name for property_name in type_properties if property_name not in verified]

        type_properties = remove_private_and_protected_items(type_properties, type_)

        if len(type_properties) == 0 and len(type_attributes) == 0:
            return False

        for method_name in type_properties:
            type_method = getattr(type_, method_name, None)
            dependency_method = getattr(dep_klass, method_name, None)

            if type_method is None or not inspect.isfunction(type_method):
                continue

            if dependency_method is None or not inspect.isfunction(dependency_method):
                is_compatible = False
                break

            dep_signature = get_type_hints(dependency_method)
            type_signature = get_type_hints(dependency_method)

            if "return" not in dep_signature:
                dep_signature["return"] = NoneType

            if "return" not in type_signature:
                type_signature["return"] = NoneType

            if type_signature != dep_signature:
                is_compatible = False
                break

        return is_compatible

    def _get_properties(
        self,
        type_: type[Any] | Callable[..., Any],
        check_dunders: bool,
        dunders_to_check: Literal["all"] | list[str] = "all",
    ) -> list[str]:
        type_properties = dir(type_)

        if not check_dunders:
            type_properties = remove_dunders(type_properties)
        else:
            if dunders_to_check != "all":
                type_properties = [
                    prop for prop in type_properties if not is_dunder(prop) or prop in dunders_to_check
                ]

        return type_properties

    def _resolve_signature(
        self,
        type_: type[Any] | Callable[..., Any],
    ) -> DependencyMapping:

        parameters = self._get_callable_parameters(type_)
        is_klass = inspect.isclass(type_)

        response: DependencyMapping = []

        for parameter in parameters.values():
            if str(parameter.kind) in ("VAR_POSITIONAL", "VAR_KEYWORD"):
                continue

            if not self._is_dependency_parameter(parameter):
                default_value = self._handle_common_parameter(parameter, is_klass=is_klass)

                if default_value is None:
                    continue

                response.append(
                    (
                        default_value,
                        [],
                    )
                )
                continue

            response.extend(self._handle_dependency_parameter(parameter))

        return response

    def _handle_dependency_parameter(
        self,
        parameter: inspect.Parameter,
    ) -> DependencyMapping:
        constructor_dependency = parameter.default

        annotation_type: Any = None
        token: str | None = None

        if isinstance(constructor_dependency, EmptyDependency):
            annotation_type = parameter.annotation
        elif isinstance(constructor_dependency, Dependency):
            annotation_type = constructor_dependency.value
            token = constructor_dependency.token

        return self.resolve(
            type_=annotation_type,
            token=token,
        )

    def _handle_common_parameter(
        self,
        parameter: inspect.Parameter,
        is_klass: bool,
    ) -> IDependency | None:
        default_value = parameter.default

        should_check_empty = is_klass

        if default_value is inspect.Parameter.empty and should_check_empty:
            raise MissingDefaultValueException(parameter.name)
        
        if not is_klass and default_value is inspect.Parameter.empty:
            return None

        dependency = Dependency(value=default_value, token=f"{parameter.name}")

        return dependency

    def _is_dependency_parameter(self, parameter: inspect.Parameter) -> bool:
        default_value = parameter.default

        return default_value is not inspect.Parameter.empty and (
            isinstance(default_value, Dependency) or isinstance(default_value, EmptyDependency)
        )

    def _get_callable_parameters(
        self, type_: type[Any] | Callable[..., Any]
    ) -> MappingProxyType[str, inspect.Parameter]:
        signature = inspect.signature(type_, eval_str=True)

        return signature.parameters
