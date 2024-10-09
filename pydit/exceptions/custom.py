class CustomException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self._message = message

    def get_message(self):
        return self._message
