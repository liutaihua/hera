# -*- coding: utf-8 -*-
import time
import gevent
from heapq import heappush

from celery.worker.job import Request
from celery.utils.functional import noop
from common.util import logger
from config.config import REVOKES_MAX, REVOKE_EXPIRES


from celery.datastructures import LimitedSet

class HeraLimitSet(LimitedSet):
    def __init__(self, maxlen=None, expires=None, data=None, heap=None):
        super(HeraLimitSet, self).__init__(maxlen, expires, data, heap)

    def add(self, key, c, heappush=heappush):
        self.purge(1, offset=1)
        inserted = time.time() + c
        self._data[key] = inserted
        heappush(self._heap, (inserted, key))

paused = HeraLimitSet(maxlen=REVOKES_MAX, expires=REVOKE_EXPIRES)

class HeraRequest(Request):
    def __init__(self, body, on_ack=noop,
                 hostname=None, eventer=None, app=None,
                 connection_errors=None, request_dict=None,
                 message=None, task=None, on_reject=noop, **opts):
        super(HeraRequest, self).__init__(body, on_ack,
                                          hostname, eventer, app,
                                          connection_errors, request_dict,
                                          message, task, on_reject, **opts
                                          )

    def paused(self):
        return self.id in paused
    
    def execute_using_pool(self, pool, **kwargs):
        '''
        check is need paused
        if is a paused task, ack the mq and create a new same task with same args
        :param pool:
        :param kwargs:
        :return:
        '''
        logger.debug('execute_using_pool, is paused: {}, task_name: {}'.format(self.paused(), self.task_name))
        if self.paused():
            itime = paused._data[self.task_id]
            if time.time() - itime > 300:
                logger.warning("pause a task larger than 300 seconds, task_id: {}".format(self.task_id))
            while time.time() < itime and self.paused():
                logger.debug("paused delay task totime -> itime: %s, id: %s" % (itime, self.task_id))
                gevent.sleep(1)
            else:
                paused.discard(self.task_id)
            # self.task.handle_pause(self.args, self.kwargs, self.task_id)
            # self.acknowledge()
            # return
            # raise TaskPausedError(self.task_id)
        super(HeraRequest, self).execute_using_pool(pool, **kwargs)

    def execute(self, loglevel=None, logfile=None):
        super(HeraRequest, self).execute(loglevel, logfile)