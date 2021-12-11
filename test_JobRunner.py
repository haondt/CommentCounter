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
def jobRunner(reddit):
    with open(TestData.ActiveJobFile, "w") as f:
        f.write(json.dumps(State()))
    yield JobRunner(FakeMutex(), TestData.ActiveJobFile, TestData.Username, reddit, commentFormatter=FakeCommentFormatter())
    # cleanup
    if os.path.exists(TestData.ActiveJobFile):
        os.remove(TestData.ActiveJobFile)

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

    def test_ignore_summon_comments(self):
        # incl parent
        return

    def test_ignore_own_comments(self):
        # TODO
        return

    def test_select_first_term_in_comment(self):
        # TODO
        return
    
    def test_match_first_term_in_summon(self):
        # TODO
        return 

    def test_count_only_top_level_comments(self):
        # TODO
        return

    def test_update_comment_counts_on_interval(self):
        # TODO
        return
    
class TestModifyJobFile:
    def test_remove_job_after_zero_remaining_updates(self):
        return

    def test_remove_new_job_with_zero_updates(self):
        return

    def test_remove_submission_with_all_jobs_new_jobs_with_zero_updates(self):
        return

    def test_remove_submission_after_zero_jobs(self):
        return

    def test_run_job_where_count_comment_removed(self):
        return

class TestInitialJobRuns:
    def test_thread_is_locked(self):
        return

    def test_thread_is_archived(self):
        return

    def test_sub_is_private(self):
        return

class TestErrorRecovery:
    def test_load_job_with_invalid_parent_comment_id(self):
        return
    
    def test_load_job_with_negative_remaining_updates(self):
        return

    def test_load_job_with_invalid_submission_id(self):
        return

    def test_load_job_with_no_terms(self):
        return
    
    def test_load_job_with_broken_data(self):
        return

    def test_load_corrupt_job_file(self):
        return
