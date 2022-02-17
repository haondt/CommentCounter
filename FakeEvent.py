class FakeEvent:
    def __init__(self, is_set=False):
        self._is_set = is_set
    def set(self):
        self._is_set = True
    def clear(self):
        self._is_set = False
    def is_set(self):
        return self._is_set
