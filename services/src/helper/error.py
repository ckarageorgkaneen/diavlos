from enum import Enum


class ErrorCode(Enum):
    pass


class ErrorData:
    _MSG_KEY = 'message'
    _STATUS_CODE_KEY = 'status_code'

    def __init__(self):
        self._dict = {}

    def __call__(self, enum):
        message = self._dict[enum][self._MSG_KEY]
        status_code = self._dict[enum][self._STATUS_CODE_KEY]
        return message, status_code

    def add(self, enum, message, status_code):
        self._dict[enum] = {
            self._MSG_KEY: message,
            self._STATUS_CODE_KEY: status_code
        }

    def add_many(self, args_list):
        for enum, message, status_code in args_list:
            self.add(enum, message, status_code)
