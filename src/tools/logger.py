import datetime
import logging
import os
from logging.handlers import RotatingFileHandler

logsDirectory = 'logs/'
formatter = logging.Formatter(
    '%(name)s :: %(asctime)s :: %(module)s :: %(funcName)s :: %(levelname)s :: %(message)s')


class Logger:
    state = True

    def __init__(self, moduleName, loggerDir=logsDirectory, format=formatter):
        self.logger = logging.getLogger(moduleName)
        self.logger.setLevel(logging.DEBUG)
        self.loggerDir = loggerDir
        self.formatter = format

        if not os.path.exists(self.loggerDir):
            os.makedirs(self.loggerDir)

        today_time = datetime.date.today()
        file_name = f"{logsDirectory}LOG_{today_time}.log"
        file_handler = RotatingFileHandler(file_name, 'a', 10000000, 1)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)

        if self.state:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.DEBUG)
            stream_handler.setFormatter(self.formatter)
            self.logger.addHandler(stream_handler)

    def getLogger(self):
        return self.logger
