import JsonExtended as json
import re
from Logger import Logger
from Models.Job import Job
from Models.State import State
import Utils


class JobLocater:
    def __init__(self, mutex, storage, username, reddit, forceRun, numUpdates=24, logger=Logger()):
        self.mutex = mutex
        self.reddit = reddit
        self._storage = storage
        self.forceRun = forceRun
        self.numUpdates = numUpdates
        self.username = username.lower()
        self._logger = logger

    def is_mention(self, comment):
        return Utils.is_mention(self.username, comment)

    def ordered_distinct(self, l):
        table = set()
        out_list = []
        for i in l:
            if i not in table:
                table.add(i)
                out_list.append(i)
        return out_list

    def try_get_terms(self, comment):
        regex = fr"(^|^.*\s)/?u/{self.username}\s*((?:[\w]+(?:/[\w]+)*(?:\s+|$))+)\s*$"
        termPart = re.match(regex, comment.body.lower())
        if termPart:
            # Split terms
            terms = re.split(r"\s+", termPart.group(2))

            # Clean the terms up a bit
            terms = [i for i in terms if len(i) > 0]

            # Split combined terms
            terms = [i.split('/') for i in terms]

            # Ensure no duplicate values in combined group of terms
            terms = [self.ordered_distinct(i) for i in terms]

            # Ensure no duplicate combined groups of terms
            term_dict = {tuple(i): i for i in terms}
            ordered_distinct_term_sets = self.ordered_distinct(term_dict.keys())
            terms = [term_dict[i] for i in ordered_distinct_term_sets]

            return len(terms) > 0, terms
        return False, None

    def Run(self):
        for comment in self.reddit.inbox.stream():
            # Filter out non-mentions and PMs
            try:
                if self.is_mention(comment):
                    comment.mark_read()
                    # Get terms from comment
                    valid, terms = self.try_get_terms(comment)
                    if valid:
                        # acquire mutex
                        self.mutex.acquire()

                        state = None
                        rewriteActiveJobs = False
                        state = self._storage.GetState()
                        # Add a new job for the comment we are replying to
                        parentId = comment.id
                        submissionId = comment.submission.id
                        self._logger.log(f"locating job for {submissionId}|{parentId}")
                        if submissionId not in state.submissions:
                            state.submissions[submissionId] = {}
                            self._logger.log(f"added entry for submission id {submissionId}")
                        if parentId not in state.submissions[submissionId]:
                            newJob = Job()
                            newJob.RemainingUpdates = self.numUpdates
                            newJob.Terms = terms
                            state.submissions[submissionId][parentId] = newJob
                            rewriteActiveJobs = True
                            self._logger.log(f"added job for parent id {parentId}")

                        if rewriteActiveJobs:
                            self._logger.log("Writing to active job file")
                            self._storage.SetState(state)

                        self.mutex.release()

                        if rewriteActiveJobs:
                            self.forceRun()
            except Exception as e:
                self._logger.log_error("Exception while locating job", e)
                try:
                    comment.mark_read()
                except Exception as e2:
                    self._logger.log_error("Exception while trying to mark comment as read", e2)

