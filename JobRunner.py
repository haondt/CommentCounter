from datetime import timedelta
import time
from CommentFormatter import CommentFormatter
import re
import numpy as np
from Logger import Logger
import Utils
from Models.State import State

class JobRunner:
    def __init__(self, run_event, mutex, storage, username, reddit, updateInterval=timedelta(hours=1), commentFormatter=CommentFormatter(), logger=Logger()):
        self._run_event = run_event
        self.mutex = mutex
        self._storage = storage
        self.reddit = reddit
        self._updateInterval = updateInterval
        self.username = username.lower()
        self.commentFormatter = commentFormatter
        self._logger = logger

    # Return a matrix where each row represents one comment,
    # And each column is a term. Each cell represents if
    # that comment contains that term.
    # Comments in ignore_comments will be a row full of False
    def CountTheComments(self, comments, terms, ignore_comments):
        countMatrix = []
        for term in terms:
            termVector = []
            regex = re.compile(
                fr".*\b{term}\b",
                (re.I | re.S)
            )
            for comment in comments:
                try:
                    if comment.body is None or comment.id in ignore_comments or Utils.is_mention(self.username, comment):
                        termVector.append(False)
                    else:
                        termVector.append(bool(regex.match(comment.body)))
                except Exception as e:
                    self._logger.log_error("Error when counting terms in comment:", e)
                    termVector.append(False)

            countMatrix.append(termVector)
        # transpose
        countMatrix = [*zip(*countMatrix)]
        return np.array(countMatrix)

    def _flatten(self, l, n):
        if n == 0:
            return l
        return self._flatten([j for i in l for j in i], n-1)


    def RunJobs(self, onlyRunNewJobs=False):
        try:
            state = self._storage.GetState()
        except Exception as e:
            self._logger.log_error("Error while getting state", e)
            state = State()
            self._storage.SetState(state)

        try:
            for sid in state.submissions:
                self._logger.log(f"Running jobs for submission {sid}")
                # Get jobs to update
                jobTuples = []
                jobs_to_remove = set()
                for pid in state.submissions[sid]:
                    job = state.submissions[sid][pid]
                    if (not onlyRunNewJobs) or (job.CountCommentId is None):
                        parentComment = self.reddit.comment(id=pid)
                        if job.RemainingUpdates <= 0:
                            jobs_to_remove.add(pid)
                        else:
                            jobTuples.append((job, parentComment))

                if (len(jobTuples) > 0):
                    try:
                        # Fetch the comments
                        submission = self.reddit.submission(sid)
                        submission.comments.replace_more(limit=0)

                        # amalgamate all the terms from all active jobs for this submission
                        allTerms = [j.Terms for (j, c) in jobTuples]
                        allTerms = self._flatten(allTerms, 2)
                        allTerms = [i for i in set(allTerms) if i is not None and len(i) > 0]

                        if len(allTerms) > 0:
                            ignored_comment_ids = []
                            for (job, parentComment) in jobTuples:
                                if job.CountCommentId is not None:
                                    ignored_comment_ids.append(job.CountCommentId)
                                ignored_comment_ids.append(parentComment.id)

                            # Count the comments
                            counts = self.CountTheComments(submission.comments, allTerms, set(ignored_comment_ids))

                            for (job, parentComment) in jobTuples:
                                self._logger.log(f"Updating comment for parent {parentComment.id} ({job.RemainingUpdates} remaining)")
                                # Form the comment
                                commentStr = self.commentFormatter.format(counts, job.Terms, np.array(allTerms), job.RemainingUpdates-1)

                                # Edit existing comment
                                if (job.CountCommentId is not None):
                                    try:
                                        countComment = self.reddit.comment(id=job.CountCommentId)
                                        countComment.edit(commentStr)
                                    except Exception as e:
                                        self._logger.log_error("Exception while trying to edit count comment: ", e)
                                # Reply to parent
                                else:
                                    try:
                                        countComment = parentComment.reply(commentStr)
                                        job.CountCommentId = countComment.id
                                    except Exception as e:
                                        self._logger.log_error("Exception while trying to reply to parent: ", e)

                                # decrease the counter
                                job.RemainingUpdates -= 1

                                if job.RemainingUpdates <= 0:
                                    jobs_to_remove.add(parentComment.id)
                        else:
                            for (job, parentComment) in jobTuples:
                                job.RemainingUpdates -= 1

                                if job.RemainingUpdates <= 0:
                                    jobs_to_remove.add(parentComment.id)


                    except Exception as e:
                        self._logger.log_error("Exception while trying to run job: ", e)
                        state.submissions[sid] = {}


                # Remove expired jobs
                for pid in jobs_to_remove:
                    state.submissions[sid].pop(pid)

            # remove states with no jobs
            for sid in [i for i in state.submissions]:
                if len(state.submissions[sid]) == 0:
                    state.submissions.pop(sid)
        except Exception as e:
            self._logger.log_error("Exception while reading state... resetting state", e)
            state = State()

        # Update active jobs file
        self._storage.SetState(state)

    def run(self):
        self._logger.log("Starting")
        while not self._run_event.is_set():
            self.mutex.acquire()
            self.RunScheduledJobs()
            self.mutex.release()
            self._logger.log(f"Waiting {self._updateInterval.total_seconds()}s for next run")
            self._run_event.wait(self._updateInterval.total_seconds())
        self._logger.log("Stopping")

    # Run only jobs that have never been run before
    def RunNewJobs(self):
        self._logger.log("Running new jobs")
        self.RunJobs(True)

    # Run all jobs
    def RunScheduledJobs(self):
        self._logger.log("Running scheduled jobs")
        self.RunJobs(False)
