from pydit.adapters.logging.interfaces.logger import LoggerInterface
from pydit.factories.logging import get_logging_factory


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

    return logger_class.get_instance(name)
