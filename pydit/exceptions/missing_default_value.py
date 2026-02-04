from pydit.exceptions.custom import CustomException


class MissingDefaultValueException(CustomException):
    def __init__(self, parameter_name: str):
        super().__init__(f"Can't resolve signature: Parameter '{parameter_name}' has no default value assigned")
        self.__parameter_name = parameter_name

    @property
    def parameter_name(self) -> str:
        return self.__parameter_name
