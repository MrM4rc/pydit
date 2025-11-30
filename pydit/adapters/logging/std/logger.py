from logging import Logger, getLogger
from pydit.adapters.logging.interfaces.logger import LoggerInterface


class PythonLoggerAdapter(LoggerInterface):
    _logger: Logger

    def __init__(self, name: str) -> None:
        self._logger = getLogger(name)

    @staticmethod
    def get_instance(name: str) -> LoggerInterface:
        return PythonLoggerAdapter(name)

    def debug(self, message: str) -> None:
        self._logger.debug(message)

    def info(self, message: str) -> None:
        self._logger.info(message)

    def warning(self, message: str) -> None:
        self._logger.warning(message)

    def error(self, message: str) -> None:
        self._logger.error(message)

    def disable(self) -> None:
        """Disable the logger."""
        self._logger.propagate = False
