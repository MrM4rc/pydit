from pydit.adapters.logging.interfaces.logger import LoggerInterface
from pydit.factories.logging.type import LoggingFactory


class PythonLoggingFactory(LoggingFactory):
    @property
    def logger(self) -> type[LoggerInterface]:
        from pydit.adapters.logging.std.logger import PythonLoggerAdapter

        return PythonLoggerAdapter
