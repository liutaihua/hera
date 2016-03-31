# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

from kombu.async.timer import to_timestamp
from kombu.utils.encoding import safe_repr

from celery.utils.timeutils import timezone
# from celery.worker.job import Request
from common.hera_job import HeraRequest as Request
from celery.worker.state import task_reserved
from celery.worker.job import revoked_tasks

from config.app_config import REVOKES_MAX
# from common.util import logger
from common.hera_job import paused

__all__ = ['hera_strategy']

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


def hera_strategy(task, app, consumer,
            info=logger.info, error=logger.error, task_reserved=task_reserved,
            to_system_tz=timezone.to_system):
    hostname = consumer.hostname
    eventer = consumer.event_dispatcher
    Req = Request
    connection_errors = consumer.connection_errors
    _does_info = logger.isEnabledFor(logging.INFO)
    events = eventer and eventer.enabled
    send_event = eventer.send
    call_at = consumer.timer.call_at
    apply_eta_task = consumer.apply_eta_task
    rate_limits_enabled = not consumer.disable_rate_limits
    get_bucket = consumer.task_buckets.__getitem__
    handle = consumer.on_task_request
    limit_task = consumer._limit_task

    def task_message_handler(message, body, ack, reject, callbacks,
                             to_timestamp=to_timestamp):
        req = Req(body, on_ack=ack, on_reject=reject,
                  app=app, hostname=hostname,
                  eventer=eventer, task=task,
                  connection_errors=connection_errors,
                  message=message)
        # do check revoke purge befor task handler, skip the expired revoke
        revoked_tasks.purge(limit=None, offset=REVOKES_MAX)
        # paused.purge(limit=None, offset=REVOKES_MAX)
        if req.revoked():
            return

        if _does_info:
            logger.info('hera Received task: %s', req)

        if events:
            send_event(
                'task-received',
                uuid=req.id, name=req.name,
                args=safe_repr(req.args), kwargs=safe_repr(req.kwargs),
                retries=req.request_dict.get('retries', 0),
                eta=req.eta and req.eta.isoformat(),
                expires=req.expires and req.expires.isoformat(),
            )

        if req.eta:
            try:
                if req.utc:
                    eta = to_timestamp(to_system_tz(req.eta))
                else:
                    eta = to_timestamp(req.eta, timezone.local)
            except OverflowError as exc:
                error("Couldn't convert eta %s to timestamp: %r. Task: %r",
                      req.eta, exc, req.info(safe=True), exc_info=True)
                req.acknowledge()
            else:
                consumer.qos.increment_eventually()
                call_at(eta, apply_eta_task, (req, ), priority=6)
        else:
            if rate_limits_enabled:
                bucket = get_bucket(task.name)
                if bucket:
                    return limit_task(req, bucket, 1)
            task_reserved(req)
            if callbacks:
                [callback() for callback in callbacks]
            handle(req)

    return task_message_handler