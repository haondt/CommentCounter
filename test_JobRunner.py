from attr import has
from constantly import FlagConstant
import pytest
import FakePraw
import random
import TestData
from Models.Job import Job
from Models.State import State
from JobRunner import JobRunner
import JsonExtended as json
from FakeMutex import FakeMutex
import os
import numpy as np
from FakeCommentFormatter import FakeCommentFormatter
from test_JobLocator import jobLocator
from Storage import MemoryStorage as Storage

np.set_printoptions(precision=2, suppress=True, )

FakePraw.State.Username = TestData.Username

@pytest.fixture()
def reddit():
    # instantiate fake reddit
    reddit = FakePraw.Reddit('bot1')

    # Create some submissions
    submissions = [reddit._create_submission("","") for _ in range(5)]

    yield reddit

@pytest.fixture()
def storage():
    storage = Storage(State())
    yield storage
    storage.DeleteState()

@pytest.fixture()
def jobRunner(reddit, storage):
    yield JobRunner(FakeMutex(), storage, TestData.Username, reddit, commentFormatter=FakeCommentFormatter())

class MinimalComment:
    def __init__(self, body):
        self.body = body
        self.submission = None
        self.id = str(random.randint(0,1000000))

class TestCollectComments:
    def test_count_comments(self, jobRunner):
        # Create list of valid comments
        comments = [MinimalComment(i[0]) for i in TestData.CommentsTermPairs]
        comment_terms = [set(i[1]) for i in TestData.CommentsTermPairs]

        # Get all terms mentioned in comments
        terms = list(set([k for j in [i[1] for i in TestData.CommentsTermPairs] for k in j]))

        key = [[j in i for j in terms] for i in comment_terms]
        result = jobRunner.CountTheComments(comments, terms, [])

        assert np.all(key == result)

    def test_run_job(self, jobRunner, reddit, storage):
        # Create list of valid comments
        submission = reddit._create_submission("", "submitter")
        summon_comment = "/u/CountTheComments Rem Ram Felix"
        comments = [
            submission.reply(summon_comment, "summoner"), # should ignore parent comment
            submission.reply("/u/CountTheComments Ram", "second_summoner"), # should ignore summon comments
            submission.reply("comment rem ram", "a"),
            submission.reply("comment Felix", "b"),
            submission.reply("comment", "c"),
            submission.reply("REM", "d")
        ]
        terms = [["Rem"], ["RAM"], ["felix"], ["puck"]]

        # Create job
        job = Job()
        job.RemainingUpdates = 1
        job.Terms = terms

        # Write job to file
        state = storage.GetState()
        state.submissions[submission.id] = {}
        state.submissions[submission.id][comments[0].id] = job
        storage.SetState(state)

        # run job
        jobRunner.RunScheduledJobs()
        counts = jobRunner.commentFormatter.Counts.pop()

        has_any_terms = np.any(counts, axis=1)
        assert np.all(np.equal(has_any_terms, np.array([False, False, True, True, False, True])))

    def test_dont_count_ignore_comments(self, jobRunner):
        # Create list of valid comments
        comments = [MinimalComment(i[0]) for i in TestData.CommentsTermPairs]
        comment_terms = [set(i[1]) for i in TestData.CommentsTermPairs]

        # Get all terms mentioned in comments
        terms = list(set([k for j in [i[1] for i in TestData.CommentsTermPairs] for k in j]))

        # randomly select 50% of comments to be ignored
        ignored_indices = np.array(random.sample(list(range(len(comments))), len(comments)//2))
        ignored_ids = [comments[i].id for i in ignored_indices]

        key = np.array([np.array([j in i for j in terms]) for i in comment_terms])
        key[ignored_indices] = False
        result = jobRunner.CountTheComments(comments, terms, set(ignored_ids))

        assert np.all(key == result)

    def test_ignore_own_comments(self, reddit, jobRunner, storage):
        # Create list of valid comments
        submission = reddit._create_submission("", "submitter")
        summon_comment1 = submission.reply("/u/CountTheComments Rem Ram", "summoner1")
        summon_comment2 = submission.reply("/u/CountTheComments Felix Ram", "summoner2")
        submission.reply("rem ram felix")

        # Create job 1
        job1 = Job()
        job1.RemainingUpdates = 1
        job1.Terms = [["rem", "ram"]]

        job2 = Job()
        job2.RemainingUpdates = 1
        job2.Terms = [["felix", "ram"]]

        # Write jobs to file
        state = storage.GetState()
        state.submissions[submission.id] = {}
        state.submissions[submission.id][summon_comment1.id] = job1
        state.submissions[submission.id][summon_comment2.id] = job2
        storage.SetState(state)

        # run jobs
        jobRunner.RunScheduledJobs()
        counts2 = jobRunner.commentFormatter.Counts.pop()
        counts1 = jobRunner.commentFormatter.Counts.pop()

        has_any_terms1 = np.any(counts1, axis=1)
        has_any_terms2 = np.any(counts2, axis=1)

        assert np.all(np.equal(has_any_terms1, np.array([False, False, True])))
        assert np.all(np.equal(has_any_terms2, np.array([False, False, True])))

    def test_update_comment_counts_on_interval(self, reddit, jobRunner, storage):
        submission = reddit._create_submission("", "submitter")
        summon_comment = submission.reply("/u/CountTheComments Rem Ram", "summoner")
        submission.reply("rem ram felix")

        # Create job
        job = Job()
        job.RemainingUpdates = 2
        job.Terms = [["rem"]]

        # Write job to file
        state = storage.GetState()
        state.submissions[submission.id] = {}
        state.submissions[submission.id][summon_comment.id] = job
        storage.SetState(state)

        # run job
        jobRunner.RunScheduledJobs()
        counts = jobRunner.commentFormatter.Counts.pop()
        has_any_terms = np.any(counts, axis=1)
        assert np.all(np.equal(has_any_terms, np.array([False, True])))

        # add comment
        submission.reply("rem ram felix")

        # run job again
        jobRunner.RunScheduledJobs()
        counts = jobRunner.commentFormatter.Counts.pop()
        has_any_terms = np.any(counts, axis=1)
        assert np.all(np.equal(has_any_terms, np.array([False, True, True])))

    def test_count_invalid_comment(self, reddit, jobRunner):
        submission = reddit._create_submission("", "submitter")

        counts = jobRunner.CountTheComments([
            submission.reply("/u/CountTheComments Rem Ram", "summoner"),
            submission.reply("rem ram felix"),
            submission.reply(None)
        ], [["rem", "ram"]], set([]))

        has_any_terms = np.any(counts, axis=1)
        assert np.all(np.equal(has_any_terms, np.array([False, True, False])))

    def test_wont_run_jobs_with_zero_remaining_updates(self, jobRunner, reddit, storage):
        submission = reddit._create_submission("", "submitter")
        summon_comment = submission.reply("/u/CountTheComments Rem Ram", "summoner")
        submission.reply("rem ram felix")

        # Create job
        job = Job()
        job.RemainingUpdates = 0
        job.Terms = [["rem"]]

        # Write job to file
        state = storage.GetState()
        state.submissions[submission.id] = {}
        state.submissions[submission.id][summon_comment.id] = job
        storage.SetState(state)

        # run job
        jobRunner.RunScheduledJobs()
        assert len(jobRunner.commentFormatter.Counts) == 0

class TestModifyJobFile:
    def test_remove_job_after_zero_remaining_updates(self, jobRunner, reddit, storage):
        submission = reddit._create_submission("", "submitter")

        # Create job
        job = Job()
        job.RemainingUpdates = 2
        job.Terms = [["rem"]]
        summon_comment = submission.reply("/u/countthecomments", "foo")

        job2 = Job()
        job2.RemainingUpdates = 5
        job2.Terms = [["ram"]]

        # Write job to file
        state = storage.GetState()
        state.submissions[submission.id] = {}
        state.submissions[submission.id][summon_comment.id] = job
        state.submissions[submission.id][submission.reply("/u/countthecomments", "foo").id] = job2
        storage.SetState(state)

        # Run job
        jobRunner.RunScheduledJobs()
        jobRunner.RunScheduledJobs()

        # Check job file has been cleaned out
        state = storage.GetState()
        assert len(state.submissions[submission.id]) == 1
        assert summon_comment.id not in state.submissions[submission.id]

    def test_remove_job_after_zero_remaining_updates_on_first_run(self, jobRunner, reddit, storage):
        submission = reddit._create_submission("", "submitter")

        # Create job
        job = Job()
        job.RemainingUpdates = 1
        job.Terms = [["rem"]]
        summon_comment = submission.reply("/u/countthecomments", "foo")

        job2 = Job()
        job2.RemainingUpdates = 5
        job2.Terms = [["ram"]]

        # Write job to file
        state = storage.GetState()
        state.submissions[submission.id] = {}
        state.submissions[submission.id][summon_comment.id] = job
        state.submissions[submission.id][submission.reply("/u/countthecomments", "foo").id] = job2
        storage.SetState(state)

        # Run job
        jobRunner.RunScheduledJobs()

        # Check job file has been cleaned out
        state = storage.GetState()
        assert len(state.submissions[submission.id]) == 1
        assert summon_comment.id not in state.submissions[submission.id]


    def test_remove_new_job_with_zero_updates(self, jobRunner, reddit, storage):
        submission = reddit._create_submission("", "submitter")

        # Create job
        job = Job()
        job.RemainingUpdates = 0
        job.Terms = [["rem"]]
        summon_comment = submission.reply("/u/countthecomments", "foo")

        job2 = Job()
        job2.RemainingUpdates = 5
        job2.Terms = [["ram"]]

        # Write job to file
        state = storage.GetState()
        state.submissions[submission.id] = {}
        state.submissions[submission.id][summon_comment.id] = job
        state.submissions[submission.id][submission.reply("/u/countthecomments", "foo").id] = job2
        storage.SetState(state)

        # Run job
        jobRunner.RunScheduledJobs()

        # Check job file has been cleaned out
        state = storage.GetState()
        assert len(state.submissions[submission.id]) == 1
        assert summon_comment.id not in state.submissions[submission.id]

    def test_remove_submission_after_zero_jobs(self, jobRunner, reddit, storage):
        submission = reddit._create_submission("", "submitter")

        # Create job
        job = Job()
        job.RemainingUpdates = 2
        job.Terms = [["rem"]]
        summon_comment = submission.reply("/u/countthecomments", "foo")

        job2 = Job()
        job2.RemainingUpdates = 3
        job2.Terms = [["ram"]]

        # Write job to file
        state = storage.GetState()
        state.submissions[submission.id] = {}
        state.submissions[submission.id][summon_comment.id] = job
        state.submissions[submission.id][submission.reply("/u/countthecomments", "foo").id] = job2
        storage.SetState(state)

        # Run job
        jobRunner.RunScheduledJobs()
        jobRunner.RunScheduledJobs()
        jobRunner.RunScheduledJobs()

        # Check job file has been cleaned out
        state = storage.GetState()
        assert submission.id not in state.submissions

    def test_remove_submission_with_all_jobs_new_jobs_with_zero_updates(self, reddit, jobRunner, storage):
        submission = reddit._create_submission("", "submitter")

        # Create job
        job = Job()
        job.RemainingUpdates = 0
        job.Terms = [["rem"]]

        job2 = Job()
        job2.RemainingUpdates = 0
        job2.Terms = [["ram"]]

        # Write job to file
        state = storage.GetState()
        state.submissions[submission.id] = {}
        state.submissions[submission.id][submission.reply("/u/countthecomments", "bar").id] = job
        state.submissions[submission.id][submission.reply("/u/countthecomments", "foo").id] = job2
        storage.SetState(state)

        # Run job
        jobRunner.RunScheduledJobs()
        jobRunner.RunScheduledJobs()
        jobRunner.RunScheduledJobs()

        # Check job file has been cleaned out
        state = storage.GetState()
        assert submission.id not in state.submissions

    def test_run_job_where_count_comment_removed(self):
        return

    def test_run_job_where_summon_comment_removed(self):
        return

    def test_run_job_where_submission_removed(self):
        return

class TestErrorRecovery:
    def test_thread_is_locked(self):
        return

    def test_thread_is_archived(self):
        return

    def test_sub_is_private(self):
        return
    # - author null = removed or deleted -> doesn't matter unless this is the count comment
    # - body null
    # - fetching comment body, editing comment, fetching submission, or otherwise interacting with the api creates exception
    #   - should still recover and decrement counter
    def test_load_job_with_invalid_comment_to_count_id(self):
        return

    def test_load_job_with_invalid_count_comment_id(self):
        return

    def test_load_job_with_invalid_parent_comment_id(self):
        return

    def test_load_job_with_invalid_submission_id(self):
        return

    def test_load_job_with_negative_remaining_updates(self):
        return

    def test_load_job_with_no_terms(self):
        return

    def test_load_job_with_broken_data(self):
        return

    def test_load_corrupt_job_file(self):
        return

    def test_praw_api_throws_exception(self):
        return

    def test_fetch_submission_with_no_permission(self):
        return
