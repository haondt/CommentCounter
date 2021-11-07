import praw
import threading
from JobLocater import JobLocater
from JobRunner import JobRunner

activeJobFile = "activeJobs.json"

reddit = praw.Reddit('bot1')
reddit.validate_on_submit=True

mutex = threading.Lock()

jobRunner = JobRunner(
    mutex,
    activeJobFile,
    reddit
)

jobLocater = JobLocater(
    mutex,
    activeJobFile,
    reddit,
    jobRunner.ForceRun
)

jobRunnerThread = threading.Thread(target=jobRunner.Run)
jobRunnerThread.start()
jobLocaterThread = threading.Thread(target=jobLocater.Run)
jobLocaterThread.start()