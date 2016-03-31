#coding=utf8
import etcd
from config.app_config import ETCD_HOST, ETCD_PORT, hera_etcd_settings
from redis.sentinel import Sentinel

from optparse import OptionParser
from celery.bin.worker import worker
from hera import hera_app

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


# from app_config import (ETCD_HOST, ETCD_PORT,\
#     REDIS_SENTINEL_HOST_KEY, REDIS_SENTINEL_PORT_KEY, REDIS_MASTER_NAME_KEY,\
#                         REDIS_PREFIX_KEY)



# etcd_client = etcd.Client(host=ETCD_HOST, port=ETCD_PORT, read_timeout=3)
def get_redis_client():
    pass
    # sentinel_host = etcd_client.read(REDIS_SENTINEL_HOST_KEY).value
    # sentinel_port = etcd_client.read(REDIS_SENTINEL_PORT_KEY).value
    # sentinel = Sentinel([(sentinel_host, sentinel_port)], socket_timeout=1)
    # # redis_host, redis_port = sentinel.discover_master(REDIS_MASTER_NAME_KEY)
    # redis_client = sentinel.master_for(REDIS_MASTER_NAME_KEY, socket_timeout=1)
    # return redis_client

def get_redis_prefix():
    pass
    # return etcd_client.read(REDIS_PREFIX_KEY).value


etcd_client = etcd.Client(host=ETCD_HOST, port=ETCD_PORT, read_timeout=3)
def get_amqp_url_list():
    AMQP_URLS = get_etcd_setting('RABBITMQ')
    logger.info("AMQP_URLS -->", AMQP_URLS)
    return filter(lambda x:x, AMQP_URLS.split(','))

def get_etcd_setting(s):
    assert s in hera_etcd_settings, 'not found {} in settings, please check app_config.py'.format(s)
    key = hera_etcd_settings[s]
    return etcd_client.read(key).value

def get_redis_url():
    sentinel_list = [tuple(i.split(':')) for i in get_etcd_setting('HERA_REDIS_SENTINEL').split(',')]
    redis_db = get_etcd_setting('HERA_REDIS_DB')
    sentinel = Sentinel(sentinel_list, socket_timeout=0.1)
    master_name = get_etcd_setting('HERA_REDIS_MASTERNAME')
    return 'redis://{}/{}'.format(
        ':'.join(map(str, sentinel.discover_master(master_name))),
        redis_db
    )

def get_redis_sentinels_list():
    return [tuple(i.split(':')) for i in get_etcd_setting('HERA_REDIS_SENTINEL').split(',')]

def get_redis_db():
    return get_etcd_setting('HERA_REDIS_DB')

def get_celery_option():
    w = worker(hera_app)
    parser = OptionParser(option_list=w.get_options() + w.preload_options)
    (options, _) = parser.parse_args()
    return options


def sprintf_result(response, retries=0):
    if not response:
        return {}
    return {"url": response.url,
            "status_code": response.status_code,
            "retries": retries,
            }