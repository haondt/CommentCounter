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
    class MinimalPM:
        def __init__(self, body):
            self.body = body

    def test_valid_mentions(self, emptyJobLocator):
        for body in TestData.SummonComments + TestData.InvalidSummonComments:
            comment = TestRegex.MinimalComment(body)
            if not emptyJobLocator.is_mention(comment):
                fail(f"Did not consider \"{body}\" a valid mention")

    # Mention is not formatted correctly, message is inbox due to a comment reply
    def test_invalid_mentions(self, emptyJobLocator):
        for body in TestData.ReplyComments:
            comment = TestRegex.MinimalComment(body)
            if emptyJobLocator.is_mention(comment):
                fail(f"Considered \"{body}\" a valid mention")

    # Ignore pms
    def test_ignore_pms(self, emptyJobLocator):
        for body in TestData.PMs:
            pm = TestRegex.MinimalPM(body)
            if emptyJobLocator.is_mention(pm):
                fail(f"Considered pm a valid mention")

    # Good mention, but terms are either formatted incorrectly or not present
    def test_invalid_summons(self, emptyJobLocator):
        for body in TestData.InvalidSummonComments:
            comment = TestRegex.MinimalComment(body)
            if emptyJobLocator.is_mention(comment):
                sucess, terms = emptyJobLocator.try_get_terms(comment)
                if sucess:
                    fail(f"Sucessfully recovered terms {terms} from summon \"{body}\"")
    
    # Get the terms correctly and remove duplicates as necessary
    def test_parse_terms(self, emptyJobLocator):
        for pair in TestData.SummonCommentPairs:
            comment = TestRegex.MinimalComment(pair[0])
            valid, terms = emptyJobLocator.try_get_terms(comment)
            if valid:
                if terms != pair[1]:
                    fail(f"Failed to gather terms {pair[1]} from summon {comment.body}.\n Found instead {terms}")
            else:
                fail(f"Failed to recover terms from summon \"{comment.body}\"")

class TestAddJobs:
    def test_add_job(self):
        return

    def test_add_jobs_for_same_submission(self):
        return

    def test_add_jobs_for_different_submissions(self):
        return