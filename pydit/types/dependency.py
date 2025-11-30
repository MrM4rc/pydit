from typing import Any, Protocol


class Dependency(Protocol):
    value: Any
    """
    Description:
        The value that will be injected.

        If value is instantiable, the constructor method will be called
    """
    token: str
    """
    Description:
        Can be used to get dependencies via token injection.

    >>> @inject(token="my_deps")
    >>> def foo(self) -> MyDepsClass:
    >>>     pass
    """
