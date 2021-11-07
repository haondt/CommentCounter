from datetime import timedelta
import time
import json
from Models import Job

class JobRunner:
    def __init__(self, mutex, activeJobsFile, reddit, updateInterval=timedelta(hours=1)):
        self.mutex = mutex
        self.activeJobsFile = activeJobsFile
        self.reddit = reddit
        self.updateInterval = updateInterval

    # Run only new jobs
    def RunNewJobs(self):
        print("Force running jobs")
        self.mutex.acquire()
        
        activeJobs = None
        with open(self.activeJobsFile, "r") as f:
            activeJobs = json.loads(f.read())

            for submissionId in activeJobs:
                # count comments
                # make sure to use submission.comments.replace_more(limit=0)
                # TODO also ignore parent comment when counting
                body = ""
                for parentId in activeJobs[submissionId]:
                    jobJson = activeJobs[submissionId][parentId]
                    job = Job(**jobJson)

                    # Only run new jobs
                    if job.CountCommentId is None:
                        parentComment = self.reddit.comment(id=parentId)
                        job.ParentCommentId = parentComment.id

                        countComment = parentComment.reply(body)
                        job.CountCommentId = countComment.id

                        # Save updated job
                        activeJobs[submissionId][parentId] = json.dumps(job)

                    if job.RemainingUpdates <= 0:
                        activeJobs[submissionId].pop(parentId)
                if len(activeJobs[submissionId]) == 0:
                    activeJobs.pop(submissionId)
            
            # Update active jobs file
            with open(self.activeJobsFile, "w") as f:
                f.write(json.dumps(activeJobs))
            
        self.mutex.release()

    def Run(self):
        self.mutex.acquire()
        print("Running jobs")
        self.mutex.release()



    # Run only pre-existing jobs
    def RunScheduledJobs(self):
        print("Running jobs")
        self.mutex.acquire()
        
        activeJobs = None
        with open(self.activeJobsFile, "r") as f:
            activeJobs = json.loads(f.read())

            for submissionId in activeJobs:
                # count comments
                # make sure to use submission.comments.replace_more(limit=0)
                # TODO also ignore parent AND own pre-existing comment when counting (check author)
                body = ""
                for parentId in activeJobs[submissionId]:
                    jobJson = activeJobs[submissionId][parentId]
                    job = Job(**jobJson)

                    # Only run pre-existing jobs
                    if job.CountCommentId is not None:
                        # TODO Find comment and edit it with body

                        job.RemainingUpdates -= 1

                        # Save updated job
                        activeJobs[submissionId][parentId] = json.dumps(job)

                    if job.RemainingUpdates <= 0:
                        activeJobs[submissionId].pop(parentId)
                if len(activeJobs[submissionId]) == 0:
                    activeJobs.pop(submissionId)
            
            # Update active jobs file
            with open(self.activeJobsFile, "w") as f:
                f.write(json.dumps(activeJobs))
            
        self.mutex.release()