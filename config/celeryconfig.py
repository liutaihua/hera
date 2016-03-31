import os
import sys
from common.util import get_amqp_url_list, get_etcd_setting
from common.util import get_redis_url
from common.util import get_redis_db
from common.util import get_redis_sentinels_list
from common.util import get_celery_option
from common.util import logger
options = get_celery_option()
sys.path.insert(0, os.getcwd())

from common.sentinel import register_redis_sentinel
register_redis_sentinel("redis-sentinel")


BROKER_URL = get_amqp_url_list()
# the amqp of broker setting, just keep the default value
CELERY_DEFAULT_EXCHANGE = 'celery'
CELERY_DEFAULT_EXCHANGE_TYPE = 'direct'
CELERY_DEFAULT_ROUTING_KEY = 'celery'
CELERY_DEFAULT_DELIVERY_MODE = 'persistent'  # or 'transient'

# if need long long expires time, maybe should use redis as the result backend store
if options.result_backend == 'redis':
    logger.info('######################## use redis as the result store ########################')
    # CELERY_RESULT_BACKEND = get_redis_url()
    CELERY_RESULT_BACKEND = 'redis-sentinel'
    # fmt: [('192.168.1.217', 16379), ('192.168.1.217', 16379), ('192.168.1.217', 16379)]
    REDIS_SENTINEL_SENTINELS = get_redis_sentinels_list()
    REDIS_SENTINEL_MASTER_NAME = 'wmcr'
    REDIS_SENTINEL_REDIS_DB = get_redis_db()
elif options.result_backend == 'amqp':
    logger.info('######################## use amqp as the result store ########################')
    CELERY_RESULT_BACKEND = 'amqp'


CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_RESULT_EXPIRES = 86400 * 7

CELERY_STORE_ERRORS_EVEN_IF_IGNORED = True

# this value will by gevent pool size if use the gevent mod
CELERYD_CONCURRENCY = get_etcd_setting('CELERY_CONCURRENCY')
BROKER_POOL_LIMIT = 10
BROKER_CONNECTION_TIMEOUT = 3
BROKER_CONNECTION_MAX_RETRIES = 10

BROKER_HEARTBEAT = 10 # every 5 seconds heartbeat sending with amqp

CELERY_IMPORTS = ('handler.timer', 'handler.task_controller')

#admin
# CELERY_SEND_TASK_ERROR_EMAILS = True
# ADMINS = (('a', 'a@mail.com'))
# SERVER_EMAIL = 'celery'
# EMAIL_HOST = 'smtp.server.com'
# EMAIL_HOST_USER = 'username'
# EMAIL_HOST_PASSWORD = 'passwd'
# EMAIL_PORT = 25
# EMAIL_USE_SSL = False
# EMAIL_USE_TLS = False
# EMAIL_TIMEOUT = 3



