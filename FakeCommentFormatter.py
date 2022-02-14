
class FakeCommentFormatter:
    def __init__(self):
        self.Counts = []

    def format(self, counts, job_terms, all_terms, remaining_updates):
        self.Counts.append(counts)
        return ""