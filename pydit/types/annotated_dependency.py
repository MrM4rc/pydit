from typing import Generic
from typing_extensions import TypeVar

D = TypeVar("D")
Token = TypeVar("Token", bound=str | None, default=None)


class AnnotatedDependency(Generic[D, Token]):
    """
    Description:
        This type is used to inject dependencies in __init__ methods

    Example:
        >>> class Test:
        >>> def __init__(self, dep: AnnotatedDependency[str, Literal['my_token']]):
        >>>     ...
    """
