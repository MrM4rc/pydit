from pydit.exceptions.custom import CustomException


class MissingPropertyTypeException(CustomException):
    def __init__(self):
        super().__init__("Return type of property is missing")
