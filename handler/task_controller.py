#coding=utf8
import requests
from hera import hera_app
from common.models import HeraTask
from common.util import logger
from common.hera_job import paused

import celery.task.control
import celery.events.state


@hera_app.task(bind=True, base=HeraTask)
def revoke_manual(self, task_id, terminate=True):
    # celery.task.control.revoke(task_id, terminate=terminate)
    self.app.control.revoke(task_id, terminate=terminate)
    logger.info("revoke manual: {}".format(task_id))
    return {"revoed_task_id": task_id, "terminate": terminate}

@hera_app.task(bind=True, base=HeraTask)
def revoke_by_task_name(self, task_name, terminate=True):
    query = celery.events.state.State().tasks_by_type(task_name)
    for uuid, task in query:
        celery.task.control.revoke(uuid, terminate=terminate)
    return dict(query)

@hera_app.task(bind=True, base=HeraTask)
def pause_task(self, task_id):
    paused.add(task_id, 120)

@hera_app.task(bind=True, base=HeraTask)
def resume_paused_task(self, task_id):
    paused.discard(task_id)
    # paused.purge(limit=None, offset=0)