import inspect
from typing import Any, Literal, Optional, get_type_hints
from pydit.exceptions.dependency_not_found import PyDitDependencyNotFoundException
from pydit.injector.dependencies import dependencies
from pydit.types.dependency import Dependency
from pydit.utils.is_dunder import is_dunder
from pydit.utils.remove_dunders import remove_dunders


UNBIND_TYPE = "PYDIT_UNBIND_9fd66aee-e603-495e-b7d0-4366820e24c3"


class PyDit:
    def _resolve_dependencies(self, type_: Any, token: Optional[str] = None):
        pass

    def _resolve_by_subclass(
        self,
        type_: type[Any],
        *,
        check_dunders: bool = False,
        dunders_to_check: Literal["all"] | list[str] = "all",
    ) -> type[Any] | Any:
        response: type[Any] | Any = UNBIND_TYPE

        for dependency in dependencies.values():
            if not inspect.isclass(dependency.value):
                continue

            if not type_._is_protocol:
                response = dependency.value if issubclass(dependency.value, type_) else response

                if response != UNBIND_TYPE:
                    break

        if response == UNBIND_TYPE:
            raise PyDitDependencyNotFoundException

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

        type_attributes = get_type_hints(type_)
        dep_attributes = get_type_hints(dep_klass)

        type_attributes = {key: type_attributes.get(key) for key in type_properties}
        dep_attributes = {key: dep_attributes.get(key) for key in type_properties}

        if type_attributes != dep_attributes:
            return False

        for property_name in type_properties:
            type_property = getattr(type_, property_name)
            dependency_property = getattr(dep_klass, property_name)

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
