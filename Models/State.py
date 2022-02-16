import json
import copy
from Models.Job import Job
class State:
    def __init__(self):
        self.submissions = {}

    def _apply_to_all_jobs(self, f):
        for sid in self.submissions:
            for pid in self.submissions[sid]:
                self.submissions[sid][pid] = f(self.submissions[sid][pid])

    def from_dict(self, d):
        self.__dict__ = d
        def f(jd):
            j = Job()
            j.from_dict(jd)
            return j
        self._apply_to_all_jobs(lambda x: f(x))

    def to_dict(self):
        cpy = State()
        cpy.__dict__ = copy.deepcopy(self.__dict__)
        cpy._apply_to_all_jobs(lambda x: x.to_dict())
        return cpy.__dict__
