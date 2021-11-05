import pytest
import FakePraw
from JobLocater import JobLocater
import TestData
import random
from pytest import fail

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

@pytest.fixture()
def emptyJobLocator():
    return JobLocater(None, None, TestData.Username, None, None)

class TestRegex:
    class MinimalComment:
        def __init__(self, body):
            self.body = body
            self.submission = None

    def test_valid_mentions(self, emptyJobLocator):
        for body in TestData.SummonComments + TestData.InvalidSummonComments:
            if not emptyJobLocator.is_mention(TestRegex.MinimalComment(body)):
                fail(f"Did not consider \"{body}\" a valid mention")

    # Mention is not formatted correctly, message is inbox due to a comment reply
    def test_invalid_mentions(self, emptyJobLocator):
        for body in TestData.ReplyComments:
            if emptyJobLocator.is_mention(TestRegex.MinimalComment(body)):
                fail(f"Considered \"{body}\" a valid mention")

    def test_ignore_pms(self, emptyJobLocator):
        # TODO
        return

    # Good mention, but terms are either formatted incorrectly or not present
    def test_invalid_summons(self, emptyJobLocator):
        for body in TestData.InvalidSummonComments:
            comment = TestRegex.MinimalComment(body)
            if emptyJobLocator.is_mention(comment):
                sucess, terms = emptyJobLocator.try_get_terms(comment)
                if sucess:
                    fail(f"Sucessfully recovered terms {terms} from summon \"{body}\"")
    

    def test_parse_terms(self, emptyJobLocator):
        # TODO
        return

    def test_ignore_parent_comment(self, emptyJobLocator):
        # TODO
        return

    def test_ignore_own_comment(self, emptyJobLocator):
        # TODO
        return

    def test_select_first_term_in_comment(self, emptyJobLocator):
        # TODO
        return
    
    def test_match_first_term_in_summon(self, emptyJobLocator):
        # TODO
        return 