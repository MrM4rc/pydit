class CustomException(Exception):
    def __init__(self, message: str):
        self._message = message

    def get_message(self):
        return self._message
