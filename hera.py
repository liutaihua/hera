# -*- coding: utf-8 -*-
# author liutaihua(defage@gmail.com)
'''
celery的初始化app入口
'''
import os
import sys
import requests
import json
import celery
from celery import Celery

from celery.datastructures import LimitedSet
from celery.worker import state
from celery.bin import Option

from config.config import REVOKES_MAX, REVOKE_EXPIRES

state.revoked = LimitedSet(maxlen=REVOKES_MAX, expires=REVOKE_EXPIRES)

os.environ['CELERY_CONFIG_MODULE'] = 'config.celeryconfig'
hera_app = Celery()

hera_app.user_options['worker'].add(
    Option('--result-backend', dest='result_backend', default='amqp', help='amqp or redis use for store thre celery result')
)