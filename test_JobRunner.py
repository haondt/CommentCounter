class TestCollectComments:
    def test_count_comments(self):
        # TODO
        return

    def test_ignore_parent_comment(self):
        # TODO
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
