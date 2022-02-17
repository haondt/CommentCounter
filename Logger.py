from datetime import datetime
from os import pread
class Logger:
    def __init__(self, context=None):
        self._context = context

    def log(self, message):
        print(self._format(message))
    def log_error(self, message, error):
        print(self._format(f"{message}\n{error}"))

    def _format(self, message):
        parts = []
        parts.append("[" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "]")
        if self._context is not None:
            parts.append(f"[{self._context}]")

        parts.append(message)

        return " ".join(parts)