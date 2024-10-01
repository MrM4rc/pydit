import inspect
from typing import Any, Literal, Optional, get_type_hints
from pydit.exceptions.dependency_not_found import PyDitDependencyNotFoundException
from pydit.types.dependency import Dependency
from pydit.core.dependencies import dependencies
from pydit.utils.is_dunder import is_dunder
from pydit.utils.remove_dunders import remove_dunders


class DependencyResolver:
    def resolve_dependencies(self, type_: Any, token: Optional[str] = None) -> Dependency:
        dependency: Dependency | None = None

        if token:
            dependency = dependencies.get(token)

        elif inspect.isclass(type_):
            dependency = self._resolve_by_type(type_)

        if dependency is None:
            raise PyDitDependencyNotFoundException

        return dependency

    def _resolve_by_type(
        self,
        type_: type[Any],
        *,
        check_dunders: bool = False,
        dunders_to_check: Literal["all"] | list[str] = "all",
    ) -> Dependency | None:
        response: Dependency | None = None

        for dependency in dependencies.values():
            if not type_._is_protocol:
                klass = (
                    dependency.value.__class__
                    if not inspect.isclass(dependency.value)
                    else dependency.value
                )
                response = dependency if issubclass(klass, type_) else response

                if response is not None:
                    break

            if self._check_compatibility_by_annotations(
                type_, dependency, check_dunders, dunders_to_check
            ):
                response = dependency

        return response

    def _check_compatibility_by_annotations(
        self,
        type_: type[Any],
        dependency: Dependency,
        check_dunders: bool = False,
        dunders_to_check: Literal["all"] | list[str] = "all",
    ) -> bool:
        dep_klass = (
            dependency.value
            if inspect.isclass(dependency.value)
            else dependency.value.__class__
        )
        is_compatible = True

        type_properties = self._get_properties(type_, check_dunders, dunders_to_check)

        type_attributes = get_type_hints(type_)
        dep_attributes = get_type_hints(dep_klass)

        if type_attributes != dep_attributes:
            return False

        checked = type_attributes.keys()

        type_properties = [
            property_name
            for property_name in type_properties
            if property_name not in checked
        ]

        for method_name in type_properties:
            type_method = getattr(type_, method_name)
            dependency_method = getattr(dep_klass, method_name)

            if get_type_hints(type_method) != get_type_hints(dependency_method):
                return False

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
                    prop
                    for prop in type_properties
                    if not is_dunder(prop) or prop in dunders_to_check
                ]

        return type_properties
