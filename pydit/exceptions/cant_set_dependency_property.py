from pydit.exceptions.custom import CustomException


class CantSetDependencyPropertyException(CustomException):
    def __init__(self):
        super().__init__("Can't set dependency property")
