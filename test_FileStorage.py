from Storage import FileStorage
from Models.State import State
import pytest
import os

@pytest.fixture()
def filename():
    name = "testFileName.json"
    yield name
    if os.path.exists(name):
        os.remove(name)

class TestFileStorage:
    def test_create_file_if_not_exists(self, filename):
        state = State()
        state.submissions = {"abc": {}}
        state = FileStorage(filename, state).GetState()
        assert state.submissions == {"abc": {}}

    def test_use_existing_file_if_exists(self, filename):
        storage = FileStorage(filename)
        state = storage.GetState()
        state.submissions = {"abc":{}}
        storage.SetState(state)

        storage = FileStorage(filename)
        state = storage.GetState()
        assert state.submissions == {"abc":{}}

    def test_overwrite_file_if_exists(self, filename):
        storage = FileStorage(filename)
        state = State()
        state.submissions = {"abc":{}}
        storage.SetState(state)

        state = State()
        state.submissions = {"123":{}}
        storage = FileStorage(filename, state)
        state = storage.GetState()
        assert state.submissions == {"123":{}}

    def test_create_file_if_not_exists_and_no_state_given(self, filename):
        storage = FileStorage(filename)
        assert os.path.exists(filename)
