from typing import Literal
from pydit.factories.logging.python import PythonLoggingFactory
from pydit.factories.logging.type import LoggingFactory

factory_types = Literal["std"]

factories_map = {
    "std": PythonLoggingFactory,
}


def get_logging_factory(type_: factory_types) -> LoggingFactory:
    factory_class = factories_map[type_]

    return factory_class()
