from typing import Sequence
import json

class Job:
    CountCommentId: str = None
    Terms: Sequence[bool] = []
    RemainingUpdates: int = 0
    def __init__(self):
        self.CountCommentId = None
        self.Terms = []
        self.RemainingUpdates = 0
    
    def from_dict(self, d):
        self.__dict__ = d

    def to_dict(self):
        return self.__dict__