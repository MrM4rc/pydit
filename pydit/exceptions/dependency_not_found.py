from pydit.exceptions.custom import CustomException


class PyDitDependencyNotFoundException(CustomException):
    def __init__(self) -> None:
        super().__init__("Dependency was not found")
