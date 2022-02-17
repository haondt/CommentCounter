from datetime import timedelta
import praw
import threading
from CommentFormatter import CommentFormatter
from JobLocater import JobLocater
from JobRunner import JobRunner
from Logger import Logger
from Models.State import State
import JsonExtended as json
import signal
import os
from Storage import FileStorage

activeJobFile = "activeJobs.json"
username = "CountTheComments"
updateInterval = timedelta(hours=1)
numUpdates = 24

reddit = praw.Reddit('bot1')
reddit.validate_on_submit=True

mutex = threading.Lock()
run_event = threading.Event()

storage = FileStorage(activeJobFile)

jobRunner = JobRunner(
    run_event,
    mutex,
    storage,
    username,
    reddit,
    updateInterval,
    CommentFormatter(),
    Logger("Runner")
)

jobLocater = JobLocater(
    run_event,
    mutex,
    storage,
    username,
    reddit,
    jobRunner.RunNewJobs,
    numUpdates,
    Logger("Locater")
)

jobRunnerThread = threading.Thread(target=jobRunner.run)
jobLocaterThread = threading.Thread(target=jobLocater.run)

signal.signal(signal.SIGINT, lambda x, y: run_event.set())

jobRunnerThread.start()
jobLocaterThread.start()
