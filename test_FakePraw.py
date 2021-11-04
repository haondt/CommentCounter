import FakePraw
import TestData
import pytest
import time
import random
import threading
import signal
import Timeout

FakePraw.State.Username = TestData.Username


@pytest.fixture()
def reddit():
    # instantiate fake reddit
    reddit = FakePraw.Reddit('bot1')

    # Create some submissions
    submissions = [reddit._create_submission("","") for _ in range(5)]

    # Add the non-mention comments to each submission
    for submission in submissions:
        for body in TestData.Comments:
            submission.reply(body, random.choice(TestData.Authors))
    
    # populate the Inbox stream
    inboxCommentBodies = TestData.InboxComments
    for body in inboxCommentBodies:
        reddit.inbox._add_queued_comment(
            lambda body=body: random.choice(submissions).reply(body, random.choice(TestData.Authors)))

    yield reddit

class TestComments:
    def test_comments_present(self, reddit):
        all_comments = set([c.body for  c in reddit._comments.values()])
        # make sure non-mention comments are present
        nm_comments = set(TestData.Comments)
        assert len(all_comments.intersection(nm_comments)) == len(nm_comments)
        # make sure none of uninstantiated inbox comments are present
        m_comments = set(TestData.InboxComments)
        assert len(all_comments.intersection(m_comments)) == 0
    
    def test_commentForest_iterable(self, reddit):
        return # WIP
        # Create a new submission
        submission = reddit._create_submission("","")
        # Add some comments to the submission
        top_level_comments = {}
        for _ in range(5):
            comment = submission.reply("", author=random.choice(TestData.Authors))
            top_level_comments[comment.id] = comment
        
        child_comments = {}
        # Add some child comments
        for tlc in top_level_comments.keys():
            child_comments[tlc] = {}
            for _ in range(10):
                comment = top_level_comments[tlc].reply("", author=random.choice(TestData.Authors))
                child_comments[tlc][comment.id] = comment

        # Check top level comments are available in submission comment forest
        for top_level_comment in submission.comments:
            # Check child comments are available in tlc comment forest
            for child_comment in top_level_comment.replies:
                pass

    def test_commentForest_contains_all_comments(self, reddit):
        return # WIP
        # create some comments randomly
        new_comments = []
        for i in range(1000):
            parent = random.choice(reddit._submissions.values())
            if random.randint(0,1) == 0:
                parent = random.choice(reddit._comments.values())
            new_comments.append(parent.reply("a comment body", author=random.choice(TestData.Authors)))
        
        # Get all the comments using comment forests

class TestInbox:
    def test_inbox_populates_comments(self, reddit):
        # run through inbox
        Timeout.Run(lambda: [comment for comment in reddit.inbox.stream()], 0.1)

        # make sure inbox comments have been instantiated
        all_comments = set([c.body for  c in reddit._comments.values()])
        m_comments = set(TestData.InboxComments)
        assert len(all_comments.intersection(m_comments)) == len(m_comments)

    def test_inbox_returns_instantiated_comments(self, reddit):
        # run through inbox
        inbox_comments = []
        Timeout.Run(lambda: [inbox_comments.append(comment.body) for comment in reddit.inbox.stream()], 0.1)

        # make sure instantiated comments are in inbox
        inbox_comments = set(inbox_comments)
        original_comments = set(TestData.InboxComments)
        assert len(inbox_comments.intersection(original_comments)) == len(original_comments)

    def test_inbox_unread_persistence(self, reddit):
        # run through inbox twice
        inbox_comments = []
        Timeout.Run(lambda: [comment for comment in reddit.inbox.stream()], 0.1)
        Timeout.Run(lambda: [inbox_comments.append(comment.body) for comment in reddit.inbox.stream()], 0.1)

        # make sure instantiated comments are still in inbox
        inbox_comments = set(inbox_comments)
        original_comments = set(TestData.InboxComments)
        assert len(inbox_comments.intersection(original_comments)) == len(original_comments)

    def test_inbox_mark_read(self, reddit):
        # mark items in inbox as read
        Timeout.Run(lambda: [comment.mark_read() for comment in reddit.inbox.stream()], 0.1)

        # Ensure inbox is empty
        inbox_comments = []
        Timeout.Run(lambda: [inbox_comments.append(comment.body) for comment in reddit.inbox.stream()], 0.1)
        assert len(inbox_comments) == 0

            