import praw
import threading
from CommentFormatter import CommentFormatter
from JobLocater import JobLocater
from JobRunner import JobRunner
from Logger import Logger
from Models.State import State
import JsonExtended as json
import os
from Storage import FileStorage

activeJobFile = "activeJobs.json"

if not os.path.exists(activeJobFile):
    with open(activeJobFile, 'w') as f:
        f.write(json.dumps(State()))

reddit = praw.Reddit('bot1')
reddit.validate_on_submit=True

mutex = threading.Lock()

storage = FileStorage("activeJobs.json")
username = "CountTheComments"

jobRunner = JobRunner(
    mutex,
    storage,
    username,
    reddit,
    CommentFormatter(),
    Logger()
)

jobLocater = JobLocater(
    mutex,
    storage,
    username,
    reddit,
    jobRunner.RunNewJobs,
    24,
    Logger()
)

jobRunnerThread = threading.Thread(target=jobRunner.Run)
jobLocaterThread = threading.Thread(target=jobLocater.Run)

jobRunnerThread.start()
jobLocaterThread.start()

jobRunnerThread.join()
jobRunnerThread.join()
