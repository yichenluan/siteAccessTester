# -*- coding: utf-8 -*-
"""Log Handler

This file implements LogHandler class and ErrorFormat class.
"""
import os
import datetime
import time
import logging
import urlparse

import conf

__version__ = 'coroutine'
__author__ = 'huuunnnter@gmail.com'

class ErrorFormat(object):
    '''Implements a error format class for logging

    '''
    def __init__(self, e_type, url, message):
        self.e_type = e_type
        self.time = str(datetime.datetime.now())
        self.url = url
        self.message = message


class LogHandler(object):
    '''Implements a log handler class for provide a logger

    '''
    def __init__(self, domain):
        self.domain = domain
        self.filePath = self.__genFilePath()
        self.fileName = self.__genFileName()

    def __genFilePath(self):
        '''generate log file path

        '''
        filePath = conf.LOG_DIR
        if not os.path.exists(filePath):
            os.makedirs(filePath)
        return filePath

    def __genFileName(self):
        '''generate log file name

        '''
        netloc = urlparse.urlparse(self.domain).netloc
        nameDict = {
            'netloc': netloc,
            'time': str(time.time())
        }
        fileName = conf.LOG_FILE % nameDict
        return fileName

    def __genFileHandler(self):
        '''generate log file handler

        '''
        fileHandler = logging.FileHandler(
            os.path.join(self.filePath, self.fileName)
        )
        fileHandler.setLevel(logging.DEBUG)
        return fileHandler

    def getLogger(self):
        '''get logger

        '''
        logger = logging.getLogger(self.domain)
        logger.setLevel(logging.DEBUG)
        fileHandler = self.__genFileHandler()
        logger.addHandler(fileHandler)
        return logger
