# -*- coding: utf-8 -*-

class TaskPausedError(Exception):
    """The task has been revoked, so no result available."""


class IncorrectHttpResponseCode(Exception):
    def __init__(self, msg=''):
        self.msg = msg

    @property
    def message(self):
        return self.msg + " %s" % (self.__class__.__name__)

    def __str__(self):
        return self.message

class NotAvaiableRetryTimes(Exception):
    """not enough retry times"""
    def __init__(self, msg=''):
        self.msg = msg

    @property
    def message(self):
        return self.msg + " %s" % (self.__class__.__name__)