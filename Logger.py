from datetime import datetime
from os import pread
class ConsoleSink:
    def write(self, message):
        print(message)

class FileSink:
    def __init__(self, filename):
        self._filename = filename

    def write(self, message):
        with open(self._filename, "a", encoding="UTF-8") as f:
            f.write(message + "\n")

class Logger:
    def __init__(self, sinks=[], context=None):
        self._sinks = sinks
        self._context = context

    def _log(self, message):
        for sink in self._sinks:
            sink.write(message)

    def log(self, message):
        self._log(self._format(message))

    def log_error(self, message, error):
        self._log(self._format(f"{message}\n{error}"))

    def _format(self, message):
        parts = []
        parts.append("[" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "]")
        if self._context is not None:
            parts.append(f"[{self._context}]")
        parts.append(message)
        return " ".join(parts)
