from datetime import timedelta
import time
from CommentFormatter import CommentFormatter
import JsonExtended as json
from Models.Job import Job
from Models.State import State
import re
import numpy as np

class JobRunner:
    def __init__(self, mutex, activeJobsFile, username, reddit, updateInterval=timedelta(hours=1), commentFormatter=CommentFormatter()):
        self.mutex = mutex
        self.activeJobsFile = activeJobsFile
        self.reddit = reddit
        self.updateInterval = updateInterval
        self.username = username.lower()
        self.commentFormatter = commentFormatter

    def GetState(self):
        with open(self.activeJobsFile, "r") as f:
            return json.loads(f.read(), State)

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
                if comment.id in ignore_comments:
                    termVector.append(False)
                else:
                    termVector.append(bool(regex.match(comment.body)))
            countMatrix.append(termVector)
        # transpose
        countMatrix = [*zip(*countMatrix)]
        return np.array(countMatrix)
    
    def _flatten(self, l, n):
        if n == 0:
            return l
        return self._flatten([j for i in l for j in i], n-1)


    def RunJobs(self, onlyRunNewJobs=False):
        # Run only new jobs
        print("Force running jobs")
        self.mutex.acquire()
        
        state = self.GetState()

        for sid in state.submissions:
            # Get jobs to update
            jobTuples = []
            for pid in state.submissions[sid]:
                job = state.submissions[sid][pid]
                if (not onlyRunNewJobs) or (job.CountCommentId is None):
                    parentComment = self.reddit.comment(id=pid)
                    # TODO: check if parent comment is removed/deleted/etc
                    # TODO: check if subnmission is deleted/archived/removed/etc
                    if job.RemainingUpdates == 0:
                        state.submissions[sid].pop(pid)
                    else:
                        jobTuples.append((job, parentComment))
            
            if (len(jobTuples) > 0):
                # Fetch the comments
                submission = self.reddit.submission(sid)
                submission.comments.replace_more(limit=0)

                # amalgamate all the terms from all active jobs for this submission
                allTerms = [j.Terms for (j, c) in jobTuples]
                allTerms = self._flatten(allTerms, 2)
                allTerms = list(set(allTerms))

                ignored_comment_ids = []
                for (job, parentComment) in jobTuples:
                    if job.CountCommentId is not None:
                        ignored_comment_ids.append(job.CountCommentId)
                    ignored_comment_ids.append(parentComment.id)

                # Count the comments
                counts = self.CountTheComments(submission.comments, allTerms)

                for (job, parentComment) in jobTuples:
                    # Form the comment
                    commentStr = self.commentFormatter.format(counts, job.Terms, np.array(allTerms), job.RemainingUpdates-1)

                    # Edit existing comment
                    if (job.CountCommentId is not None):
                        countComment = self.reddit.comments(id=job.CountCommentId)
                        countComment.edit(commentStr)
                    # Reply to parent
                    else:
                        countComment = parentComment.reply(commentStr)
                        job.CountCommentId = countComment.id

                    # decrease the counter
                    job.RemainingUpdates -= 1

                    if job.RemainingUpdates <= 0:
                        state.submissions[sid].pop(parentComment.id)
                
        # Update active jobs file
        with open(self.activeJobsFile, "w") as f:
            f.write(json.dumps(state))
            
        self.mutex.release()


    def Run(self):
        while True:
            self.mutex.acquire()
            self.RunScheduledJobs()
            self.mutex.release()
            time.sleep(3600)

    # Run only jobs that have never been run before
    def RunNewJobs(self):
        self.RunJobs(True)

    # Run all jobs
    def RunScheduledJobs(self):
        self.RunJobs(False)