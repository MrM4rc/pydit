from pydit.adapters.logging.interfaces.logger import LoggerInterface
from pydit.factories.logging import get_logging_factory

all_loggers: list[LoggerInterface] = []


def get_logger(name: str) -> LoggerInterface:
    """
    Description:
        Get a logger with the specified name.

    Args:
        name (str): The name of the logger.

    Returns:
        LoggerInterface: The logger instance.
    """
    factory = get_logging_factory("std")

    logger_class = factory.logger

    logger = logger_class.get_instance(name)
    all_loggers.append(logger)

    return logger


def disable_all_loggers() -> None:
    for logger in all_loggers:
        logger.disable()
