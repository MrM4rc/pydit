import inspect
from time import time
from types import NoneType
from typing import Any, Literal, get_type_hints
from pydit.exceptions.dependency_not_found import PyDitDependencyNotFoundException
from pydit.types.dependency import Dependency
from pydit.core.dependencies import dependencies, subclasses_map
from pydit.utils.is_dunder import is_dunder
from pydit.utils.logging import get_logger
from pydit.utils.remove_dunders import remove_dunders
from pydit.utils.remove_private_protected import remove_private_and_protected_items


class DependencyResolver:
    def __init__(self):
        self.logger = get_logger("pydit.core.resolver")

    def resolve_dependencies(self, type_: Any, token: str | None = None) -> Dependency:
        start = time()
        dependency: Dependency | None = None

        if token:
            dependency = dependencies.get(token)

        elif inspect.isclass(type_):
            dependency = self._resolve_by_type(type_)

        if dependency is None:
            raise PyDitDependencyNotFoundException

        self.logger.debug(
            f"Resolved dependency '{dependency.token}' " f"in {round((time() - start) * 1000, 2)} ms"
        )

        return dependency

    def _resolve_by_type(
        self,
        type_: type[Any],
        *,
        check_dunders: bool = False,
        dunders_to_check: Literal["all"] | list[str] = "all",
    ) -> Dependency | None:
        response: Dependency | None = None

        is_protocol = getattr(type_, "_is_protocol", False)

        if type_ in subclasses_map:
            response = subclasses_map[type_][0]
            self.logger.debug(f"Resolved dependency by subclass map {type_}: {response}")

        if response is not None:
            return response

        for dependency in dependencies.values():
            if not is_protocol:
                klass = dependency.value.__class__ if not inspect.isclass(dependency.value) else dependency.value
                response = dependency if issubclass(klass, type_) else response

                if response is not None:
                    self.logger.debug(f"Resolved dependency by subclass {type_}: {response}")
                    break

            if self._check_compatibility_by_annotations(type_, dependency, check_dunders, dunders_to_check):
                response = dependency
                self.logger.debug(f"Resolved dependency by annotations compatibility {type_}: {response}")
                break

        return response

    def _check_compatibility_by_annotations(
        self,
        type_: type[Any],
        dependency: Dependency,
        check_dunders: bool = False,
        dunders_to_check: Literal["all"] | list[str] = "all",
    ) -> bool:
        dep_klass = dependency.value if inspect.isclass(dependency.value) else dependency.value.__class__
        is_compatible = True

        type_properties = self._get_properties(type_, check_dunders, dunders_to_check)

        type_attributes = remove_private_and_protected_items(get_type_hints(type_), type_)
        dep_attributes = remove_private_and_protected_items(get_type_hints(dep_klass), dep_klass)

        if type_attributes != dep_attributes:
            return False

        checked = type_attributes.keys()

        type_properties = [property_name for property_name in type_properties if property_name not in checked]

        type_properties = remove_private_and_protected_items(type_properties, type_)

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
        type_: type[Any],
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
