#coding=utf8
from config.config import ENABLE_CUSTOMER_STRATEGY
from util import get_redis_client, get_redis_prefix

from common.util import logger

from common.exceptions import NotAvaiableRetryTimes

if ENABLE_CUSTOMER_STRATEGY:
    redis_prefix = get_redis_prefix()

class TaskModel(object):
    '''
    处理id -> task_id的数据保存
    '''
    def __init__(self, tid):
        self._redis_key = redis_prefix + str(tid)
        self._redis = get_redis_client()
        self._data = self.load() or {}
        self._destoried = False

    def load(self):
        return self._redis.get(self._redis_key)

    def save(self):
        assert not self._destoried, "can not save a destoried task"
        return self._redis.set(self._redis_key, self._data)

    def revoke_task(self, tid):
        self._redis.delete(self._redis_key)
        self._destoried = True


import celery
from celery import Task

class HeraTask(Task):
    abstract = True
    if ENABLE_CUSTOMER_STRATEGY:
        Strategy = 'common.strategy:hera_strategy'

    def after_return(self, *args, **kwargs):
        logger.debug('Task returned: {0!r}'.format(self.request))

    def retry(self, args=None, kwargs=None, exc=None, throw=True,
              eta=None, countdown=None, max_retries=None, retry_args=None, **options):
        logger.info("handle retry argument: {}".format(retry_args))
        logger.info("already retry times: {}".format(self.request.retries))
        if len(retry_args or []) == 0:
            logger.info("task want retry, not avaiable retry times")
            if exc:
                raise NotAvaiableRetryTimes(exc.message)
            else:
                raise NotAvaiableRetryTimes
        max_retries = len(retry_args)
        idx = self.request.retries
        if idx >= max_retries:
            idx = max_retries -1
        countdown = retry_args[idx]
        super(HeraTask, self).retry(args, kwargs, exc, throw, eta, countdown, max_retries, **options)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.debug("------------failure logic------------------")

    def on_success(self, retval, task_id, args, kwargs):
        # TODO remove taskid from redis
        logger.debug("------------on success-----------")

    def handle_pause(self, args, kwargs, task_id):
        logger.debug('------------- handle pause --------------')
        logger.debug(self.name)
        logger.debug(args)
        logger.debug(kwargs)
        logger.debug(task_id)
        self.apply_async(args, countdown=30)
