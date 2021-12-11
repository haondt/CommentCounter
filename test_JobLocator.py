from Models.Job import Job
from Models.State import State
import pytest
import FakePraw
from FakeMutex import FakeMutex
from JobLocater import JobLocater
import TestData
import random
import os
import Timeout
import JsonExtended as json
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

@pytest.fixture()
def emptyJobLocator():
    return JobLocater(None, None, TestData.Username, None, None)

@pytest.fixture()
def jobLocator(reddit):
    with open(TestData.ActiveJobFile, "w") as f:
        f.write(json.dumps(State()))
    yield JobLocater(FakeMutex(), TestData.ActiveJobFile, TestData.Username, reddit, lambda: None, 24)
    # cleanup
    if os.path.exists(TestData.ActiveJobFile):
        os.remove(TestData.ActiveJobFile)

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
    def list_to_enum(self, l):
        if (isinstance(l, list)):
            return tuple(set([self.list_to_enum(i) for i in sorted(l)]))
        return l

    def test_add_job(self, jobLocator):
        # Run through inbox
        Timeout.Run(jobLocator.Run, 0.5)

        # Get counts for each comment grouped by its terms
        summons = {}
        for pair in TestData.SummonCommentPairs:
            key = self.list_to_enum(pair[1])
            if key not in summons:
                summons[key] = 0
            summons[key] += 1

        # Make sure jobs have been added for each summon comment
        state = None
        with open(TestData.ActiveJobFile, "r") as f:
            state = json.loads(f.read(), State)
            for submission in state.submissions.values():
                for job in submission.values():
                    key = self.list_to_enum(job.Terms)
                    if key not in summons:
                        fail(f"Found extraneous job for terms {job.Terms}")
                    else:
                        summons[key] -= 1

        assert all ([i == 0 for i in  summons.values()])