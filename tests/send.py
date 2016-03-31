import time
import os
import sys
from celery import uuid
from celery import Celery
import os

from celery.task.control import revoke

# app = Celery('tasks', backend='amqp', broker='amqp://celery:celery@192.168.1.7/celery')
from celery import Celery
sys.path.append("../")
os.environ['CELERY_CONFIG_MODULE'] = 'config.celeryconfig'
app = Celery()

if __name__ == "__main__":
    if '--revoke' in sys.argv:
        print 'revoke'
        app.send_task("handler.timer.revoke_manual", (sys.argv[2],))
        print 'send manual revoke'
    elif '--revoke_all' in sys.argv:
        app.send_task("timer.revoke_by_task_name", ("timer.register_callback",))
    elif '--pause' in sys.argv:
        app.send_task("handler.task_controller.pause_task", (sys.argv[2], ))
    else:
        for i in range(1):
            task_id = uuid()
            print 'task_id =>', task_id
            app.send_task("handler.timer.register_callback_v2", ({'url':"http://www.baidu.com/", \
                                                                  'method': 'get', 'data': None, 'params': None, 'retry_args': [3, 6], 'timeout': 2, 'require_json_res': True}, ),
                          task_id=task_id, countdown=3, utc=True)
        #app.send_task("tasks.hello_world", ("test",))
