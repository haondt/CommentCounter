import praw
import threading
from JobLocater import JobLocater
from JobRunner import JobRunner
from Models.State import State
import JsonExtended as json
import os

activeJobFile = "activeJobs.json"

if not os.path.exists(activeJobFile):
    with open(activeJobFile, 'w') as f:
        f.write(json.dumps(State()))

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