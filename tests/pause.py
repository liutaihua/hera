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
    app.send_task("handler.task_controller.pause_task", (sys.argv[1],))
    print 'send pause'
