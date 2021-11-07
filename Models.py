from typing import Sequence

class Job:
    CountCommentId: str = None
    ParentCommentId: str = None
    Terms: Sequence[str] = []
    RemainingUpdates: int = 0