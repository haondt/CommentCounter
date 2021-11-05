from re import sub
import time, random

class FakeState:
    def __init__(self):
        self.Username = None

State = FakeState()

def generate_id():
    return random.randint(0,1000000)

def Reddit(string):
    return FakeReddit()

class FakeReddit:
    validate_on_submit = None

    def __init__(self):
        self._submissions = {}
        self._comments = {}
        self.inbox = Inbox()

    def _create_submission(self, body, author):
        submission = Submission(self)
        self._submissions[submission.id] = submission
        return submission
    
    def comment(self, id):
        return self._comments[id]

    def submission(self, id):
        return self._submissions[id]


class Inbox():
    def __init__(self):
        self._commentQueue = []
        self._read_comments = []
        self._unread_comments = []

    def _add_queued_comment(self, queuedComment):
        self._commentQueue.append(queuedComment)

    def _add_comment(self, comment):
        comment._read = False
        self._unread_comments.append(comment)

    def _update_read_lists(self):
        updated_unread_comments = []
        for comment in self._unread_comments:
            if comment._read:
                self._read_comments.append(comment)
            else:
                updated_unread_comments.append(comment)
        self._unread_comments = updated_unread_comments

    def stream(self, checkContinue=None):
        self._update_read_lists()
        stream_comments = [i for i in self._unread_comments]
        while True:
            if checkContinue is not None:
                if not checkContinue():
                    break
            if len(stream_comments) > 0:
                yield stream_comments.pop()

            elif len(self._commentQueue) > 0:
                new_comment = self._commentQueue.pop()()
                self._add_comment(new_comment)
                yield new_comment

class Comment:
    def __init__(self, author, body, submission, parent=None):
        parent = parent or submission
        self._submission = submission
        self._parent = parent
        self._read = True

        self.id = generate_id()
        self._submission._reddit._comments[self.id] = self

        self.author = author
        self.body = body
        self.replies = CommentForest()

    def reply(self, body, author=State.Username):
        comment = Comment(author, body, self._submission, self)
        self.replies._comments.append(comment)
        return comment
    
    def mark_read(self):
        self._read = True
    

class Submission:
    def __init__(self, reddit):
        self._reddit = reddit
        self.id = generate_id()
        self.comments = CommentForest()

    def reply(self, body, author=State.Username):
        comment = Comment(author, body, self, self)
        self.comments._comments.append(comment)
        return comment



class CommentForest:
    def __init__(self):
        self._comments = []

    def replace_more(self, limit):
        pass

    def __iter__(self):
        return iter(self._comments)
