class Logger:
    def __init__(self):
        pass
    def log(self, message):
        print(message)
    def log_error(self, message, error):
        print(message, error)