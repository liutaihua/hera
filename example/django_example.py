# author liutaihua
# pip install django-celery
# document: http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html#using-celery-with-django
# get BROKER_URLS from etcd: /service/rabbitmq/celery
#     BROKER_URLS = etcd_conf.get_variable_etcd_value("CELERY_BROKER_URLS")



# task.py

# 重写 dowant/timer/task.py 类的_request_timer_service方法
import os
import datetime
from django.conf import settings
from celery import Celery

# BROKER_URLS 是rabbitmq服务的地址,逗号分隔分支多个
app = Celery('hera', broker=settings.BROKER_URLS)

#insert follow code to task.py Object
'''
eta = datetime.datetime.now() + datetime.timedelta(days=1)
countdown = 10
task = app.send_task("handler.timer.register_callback",
              (callback_url, callback_method, data, params, retry_args=[10, 30]),
              # eta=eta,
              task_id=task_id,
              countdown=countdown
              )
'''
# register a callback timer, will at date: eta call the callback_url, with your provied data and params

# revoke the callback timer
app.revoke(task_id)

# pause task
app.send_task("handler.task_controller.pause_task", (task_id, ))
#
# 关于caller自己定义task_id
# caller可以自己定义task_id, 在调用任务的时候, 指定task_id为自己的id, 这个id必须能保证唯一性,
# task_id可以在revoke一个task的使用
# --statedb=/var/run/celery/worker.state