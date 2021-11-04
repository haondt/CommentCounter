import signal

class _TimeoutException(Exception):
    pass
def _timeout_handler(signum, frame):
    raise _TimeoutException
signal.signal(signal.SIGALRM, _timeout_handler)

def Run(f, seconds):
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        f()
    except _TimeoutException:
        pass