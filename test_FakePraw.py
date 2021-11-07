import FakePraw
import TestData
import pytest
import time
import random
import threading
import signal
import Timeout

FakePraw.State.Username = TestData.Username


class TestTestData:
    def test_unique_comments(self):
        assert len(TestData.InboxComments) == len(set(TestData.InboxComments))    

class TestComments:
    @pytest.fixture()
    def reddit(self):
        # instantiate fake reddit
        reddit = FakePraw.Reddit('bot1')

        # Create some submissions
        submissions = [reddit._create_submission("",author_name=random.choice(TestData.Authors)) for _ in range(5)]

        # Add the non-mention comments to each submission
        for submission in submissions:
            for body in TestData.Comments:
                submission.reply(body, random.choice(TestData.Authors))

        yield reddit

    def test_comments_present(self, reddit):
        all_comments = set([c.body for  c in reddit._comments.values()])
        # make sure non-mention comments are present
        nm_comments = set(TestData.Comments)
        assert len(all_comments.intersection(nm_comments)) == len(nm_comments)
        # make sure none of uninstantiated inbox comments are present
        m_comments = set(TestData.InboxComments)
        assert len(all_comments.intersection(m_comments)) == 0
    
    def test_commentForest_iterable(self, reddit):
        # Create a new submission
        submission = reddit._create_submission("","")
        # Add some comments to the submission
        top_level_comments = {}
        for _ in range(5):
            comment = submission.reply("", author_name=random.choice(TestData.Authors))
            top_level_comments[comment.id] = comment
        assert len(top_level_comments) == 5
        
        child_comments = {}
        # Add some child comments
        for tlc in top_level_comments.keys():
            child_comments[tlc] = {}
            for _ in range(10):
                comment = top_level_comments[tlc].reply("", author_name=random.choice(TestData.Authors))
                child_comments[tlc][comment.id] = comment
            assert len(child_comments[tlc]) == 10

        # Check top level comments are available in submission comment forest
        child_comments_set = {i:set([j.id for j in child_comments[i].values()]) for i in child_comments.keys()}
        forest_tlc = []
        for top_level_comment in submission.comments:

            # Check child comments are available in tlc comment forest
            forest_child_comments = []
            for child_comment in top_level_comment.replies:
                forest_child_comments.append(child_comment.id)
            forest_child_comments = set(forest_child_comments)

            # Ensure all child comments are present for parent comment
            assert len(forest_child_comments.intersection(child_comments_set[top_level_comment.id])) == len(child_comments_set[top_level_comment.id])

            forest_tlc.append(top_level_comment.id)

        # Ensure all top level comments are present for submission
        assert len(set(forest_tlc).intersection(set([i.id for i in top_level_comments.values()]))) == len(top_level_comments)


    def recursively_fetch_comments(self, comment, action):
        action(comment)
        for reply in comment.replies:
            self.recursively_fetch_comments(reply, action)


    def test_commentForest_contains_all_comments(self, reddit):
        # create some comments randomly
        new_comment_ids = set()
        for i in range(1000):
            parent = random.choice(list(reddit._submissions.values()))
            if random.randint(0,1) == 0:
                parent = random.choice(list(reddit._comments.values()))
            new_comment_ids.add(parent.reply("a comment body", author_name=random.choice(TestData.Authors)).id)
        
        # Recursively get comments from comment forests
        for submission in reddit._submissions.values():
            for top_level_comment in submission.comments:
                self.recursively_fetch_comments(top_level_comment, lambda x: new_comment_ids.remove(x.id) if x.id in new_comment_ids else None)
        
        # Ensure all newly created comments were retrieved
        assert len(new_comment_ids) == 0


class TestInbox:
    @pytest.fixture()
    def reddit(self):
        # instantiate fake reddit
        reddit = FakePraw.Reddit('bot1')

        # Create some submissions
        submissions = [reddit._create_submission("","") for _ in range(5)]

        # Add the non-mention comments to each submission
        for submission in submissions:
            for body in TestData.Comments:
                submission.reply(body, author_name=random.choice(TestData.Authors))

        # populate the Inbox stream with comment replies that mention the bot
        inboxCommentBodies = TestData.InvalidSummonComments + TestData.SummonComments
        for body in inboxCommentBodies:
            reddit.inbox._add_queued_comment(
                lambda body=body: random.choice(submissions).reply(body, author_name=random.choice(TestData.Authors)))
        
        # populate the Inbox stream with pms
        for body in TestData.PMs:
            reddit.inbox._add_queued_comment(
                lambda body=body: FakePraw.PM(random.choice(TestData.Authors), body))

        # Add a comment from bot
        botcomment = submissions[0].reply("Comment from bot")

        # Populate inbox with comments that are a reply to a comment from the bot
        for body in TestData.ReplyComments:
            reddit.inbox._add_queued_comment(
                lambda body=body: botcomment.reply(body, author_name=random.choice(TestData.Authors)))

        yield reddit

    def test_inbox_populates_comments(self, reddit):
        # run through inbox
        Timeout.Run(lambda: [comment for comment in reddit.inbox.stream()], 0.1)

        # make sure inbox comments have been instantiated as reddit comments
        all_comments = set([c.body for  c in reddit._comments.values()])
        m_comments = set(TestData.InboxComments) - set(TestData.PMs)
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
        run1 = []
        run2 = []
        Timeout.Run(lambda: [run1.append(comment.body) for comment in reddit.inbox.stream()], 0.1)
        Timeout.Run(lambda: [run2.append(comment.body) for comment in reddit.inbox.stream()], 0.1)

        # make sure instantiated comments are still in inbox
        assert len(set(run1).intersection(set(run2))) == len(run1)

    def test_inbox_mark_read(self, reddit):
        # mark items in inbox as read
        Timeout.Run(lambda: [comment.mark_read() for comment in reddit.inbox.stream()], 0.1)

        # Ensure inbox is empty
        inbox_comments = []
        Timeout.Run(lambda: [inbox_comments.append(comment.body) for comment in reddit.inbox.stream()], 0.1)
        assert len(inbox_comments) == 0

    def test_pms_in_inbox(self, reddit):
        # run through inbox
        inbox_comments = []
        Timeout.Run(lambda: [inbox_comments.append(comment.body) for comment in reddit.inbox.stream()], 0.1)

        # make sure pms present
        assert len(set(inbox_comments).intersection(set(TestData.PMs))) == len(TestData.PMs)


    def test_pms_not_in_all_comments(self, reddit):
        # Run through inbox
        Timeout.Run(lambda: [comment for comment in reddit.inbox.stream()], 0.1)
        
        # Gather all comments
        assert len(set([c.body for c in reddit._comments.values()])-set(TestData.PMs)) == len(set([c.body for c in reddit._comments.values()]))


            