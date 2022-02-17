from datetime import timedelta
import praw
import threading
from CommentFormatter import CommentFormatter
from JobLocater import JobLocater
from JobRunner import JobRunner
from Logger import ConsoleSink, FileSink, Logger
from Models.State import State
import JsonExtended as json
import signal
import os
from Storage import FileStorage

activeJobFile = "activeJobs.json"
logFile = "log.txt"
username = "CountTheComments"
updateInterval = timedelta(hours=1)
numUpdates = 6


reddit = praw.Reddit('bot1')
reddit.validate_on_submit=True

mutex = threading.Lock()
run_event = threading.Event()

storage = FileStorage(activeJobFile)
consoleSink = ConsoleSink()
fileSink = FileSink(logFile)
loggerFactory = lambda x: Logger([consoleSink, fileSink], x)

jobRunner = JobRunner(
    run_event,
    mutex,
    storage,
    username,
    reddit,
    updateInterval,
    CommentFormatter(),
    loggerFactory("Runner")
)

jobLocater = JobLocater(
    run_event,
    mutex,
    storage,
    username,
    reddit,
    jobRunner.RunNewJobs,
    numUpdates,
    loggerFactory("Locater")
)

jobRunnerThread = threading.Thread(target=jobRunner.run)
jobLocaterThread = threading.Thread(target=jobLocater.run)

signal.signal(signal.SIGINT, lambda x, y: run_event.set())

jobRunnerThread.start()
jobLocaterThread.start()
