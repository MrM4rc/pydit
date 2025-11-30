from abc import abstractmethod
from pydit.adapters.logging.interfaces.logger import LoggerInterface


class LoggingFactory:
    @property
    @abstractmethod
    def logger(self) -> type[LoggerInterface]:
        raise NotImplementedError
