from Models.State import State
import JsonExtended as json
import os

class MemoryStorage:
    def __init__(self, state=None):
        self._state = state or State()
    def GetState(self):
        return self._state
    def SetState(self, state):
        self._state = state
    def DeleteState(self):
        self._state = None

class FileStorage:
    def __init__(self, fileName, state=None):
        self._fileName = fileName
        if state is None:
            if not os.path.exists(self._fileName):
                self.SetState(State())
        else:
            self.SetState(state)

    def GetState(self):
        with open(self._fileName, "r", encoding="UTF-8") as f:
            return json.loads(f.read(), State)

    def SetState(self, state):
        with open(self._fileName, "w", encoding="UTF-8") as f:
            f.write(json.dumps(state))

    def DeleteState(self):
        if os.path.exists(self._fileName):
            os.remove(self._fileName)