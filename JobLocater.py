import json
from random import paretovariate
import re
from datetime import datetime, timedelta
from Models import Job

class JobLocater:
    def __init__(self, mutex, activeJobFile, username, reddit, forceRun, numUpdates=24):
        self.mutex = mutex
        self.reddit = reddit
        self.activeJobFile = activeJobFile
        self.forceRun = forceRun
        self.numUpdates = numUpdates
        self.username = username.lower()

    def is_mention(self, comment):
        body = comment.body.lower()
        regex = fr"(^|^.*\s)/?u/{self.username}($|\s.*$)"
        return re.match(regex, body) and hasattr(comment, 'submission')

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

            return len(terms) > 0, terms
        return False, None

    def Run(self):
        for comment in self.reddit.inbox.stream():
            # Filter out non-mentions and DMs
            # TODO write tests for JR and FP for DMs
            if self.is_mention(comment):
                #comment.mark_read()
                # Get terms from comment
                valid, terms = self.try_get_terms(comment)
                if valid:
                    # acquire mutex
                    self.mutex.acquire()

                    activeJobs = None
                    rewriteActiveJobs = False
                    with open(self.activeJobFile, "r") as f:
                        activeJobs = json.loads(f.read())
                        # Add a new job for the comment we are replying to
                        parentId = str(comment.id)
                        submissionId = str(comment.submission.id)
                        print("locating job for", submissionId, parentId)
                        if submissionId not in activeJobs:
                            activeJobs[submissionId] = {}
                            print("added entry for submission id", submissionId)
                        if parentId not in activeJobs[submissionId]:
                            newJob = Job()
                            newJob.RemainingUpdates = self.numUpdates
                            newJob.Terms = terms
                            newJob.ParentCommentId = comment.id
                            activeJobs[submissionId][parentId] = newJob.__dict__
                            rewriteActiveJobs = True
                            print("added job for parent id", parentId)
                    
                    if rewriteActiveJobs:
                        with open(self.activeJobFile, "w") as f:
                            print("Writing to active job file")
                            f.write(json.dumps(activeJobs))

                    self.mutex.release()

                    if rewriteActiveJobs:
                        self.forceRun()