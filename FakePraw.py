from re import sub
import time, random


class FakeState:
    def __init__(self):
        self.Username = None

State = FakeState()

def generate_id():
    return str(random.randint(0,1000000))

def Reddit(string):
    return FakeReddit()

class FakeReddit:
    validate_on_submit = None

    def __init__(self):
        self._submissions = {}
        self._comments = {}
        self.inbox = Inbox()

    def _create_submission(self, body, author_name):
        submission = Submission(self, author_name)
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

    def stream(self):
        self._update_read_lists()
        stream_comments = [i for i in self._unread_comments]
        while True:
            if len(stream_comments) > 0:
                yield stream_comments.pop()

            elif len(self._commentQueue) > 0:
                new_comment = self._commentQueue.pop()()
                self._add_comment(new_comment)
                yield new_comment


class Comment():
    @property
    def body(self):
        if self._throw_error_on_get_body:
            raise Exception()
        return self._body

    @body.setter
    def body(self, value):
        self._body = value

    def __init__(self, author_name, body, submission, parent=None):
        parent = parent or submission
        self.submission = submission
        self._parent = parent
        self._read = True
        self._body = body

        self.id = generate_id()
        self.submission._reddit._comments[self.id] = self

        self.author = Redditor(author_name)
        self.replies = CommentForest()
        self._throw_error_on_edit = False
        self._throw_error_on_reply = False
        self._throw_error_on_get_body = False

    def reply(self, body, author_name=State.Username):
        if self._throw_error_on_reply:
            raise Exception()
        comment = Comment(author_name, body, self.submission, self)
        self.replies._comments.append(comment)
        return comment

    def edit(self, body):
        self._body = body
        if self._throw_error_on_edit:
            raise Exception()

    def mark_read(self):
        self._read = True

class PM:
    def __init__(self, author_name, body):
        self.author = Redditor(author_name)
        self._read = False
        self.id = generate_id()
        self.body = body

    def mark_read(self):
        self._read = True



class Submission:
    def __init__(self, reddit, author_name):
        self._reddit = reddit
        self.id = generate_id()
        self.comments = CommentForest()
        self.author = Redditor(author_name)

    def reply(self, body, author_name=State.Username):
        comment = Comment(author_name, body, self, self)
        self.comments._comments.append(comment)
        return comment

class CommentForest:
    def __init__(self):
        self._comments = []
        self._throw_error_on_replace_more = False

    def replace_more(self, limit):
        if self._throw_error_on_replace_more:
            raise Exception()

    def __iter__(self):
        return iter(self._comments)

class Redditor:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name
