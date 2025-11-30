from abc import abstractmethod
from typing import Protocol


class LoggerInterface(Protocol):

    @staticmethod
    @abstractmethod
    def get_instance(name: str) -> "LoggerInterface":
        raise NotImplementedError

    @abstractmethod
    def debug(self, message: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def info(self, message: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def warning(self, message: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def error(self, message: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def disable(self) -> None:
        """Disable the logger."""
        raise NotImplementedError
