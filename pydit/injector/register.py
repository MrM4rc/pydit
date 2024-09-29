import inspect
from typing import Any, Optional, cast, overload
<<<<<<<< HEAD:pydit/injector/register.py
from pydit.injector.dependencies import Dependency, dependencies
========
from pydit.core.dependencies import Dependency, dependencies
>>>>>>>> ce2f148 (feature: added dependency resolver):pydit/core/register.py


@overload
def injectable(value: type[Any], *, token: Optional[str] = None):
    pass


@overload
def injectable(value: Any, *, token: str):
    pass


def injectable(value: Any | type[Any], *, token: Optional[str] = None) -> None:
    is_klass = inspect.isclass(value)

    token_ = cast(str, value.__name__ if is_klass and token is None else token)

    dependencies[token_] = Dependency(value=value, token=token_)
