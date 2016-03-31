FAILED_TASK_RETRY_MAX_TIMES = 3
ETCD_HOST = '127.0.0.1'
ETCD_PORT = 2379

# REDIS_SENTINEL_HOST_KEY = "/service/celery/redis/sentinel/host"
# REDIS_SENTINEL_PORT_KEY = "/service/celery/redis/sentinel/port"
# REDIS_MASTER_NAME_KEY = "/service/redis/celery/mastername"
#
# REDIS_PREFIX_KEY = "/service/celery/redis/prefix"
#
#
# REDIS_HOST_KEY = "/service/celery/redis/host"
# REDIS_PORT_KEY = "/service/celery/redis/port"
# REDIS_DB_KEY = "/service/celery/redis/db"

ENABLE_CUSTOMER_STRATEGY = True

# maximum number of revokes to keep in memory.
REVOKES_MAX = 100
REVOKE_EXPIRES = 0
TASK_RESULT_STORE_PREFIX_KEY = 'hera-task-meta-'

hera_etcd_settings = {
    'CELERY_CONCURRENCY': '/config/hera/celery_concurrency',
    'RABBITMQ': '/service/rabbitmq/hera',
    'HERA_REDIS_SENTINEL': '/service/redis/hera/sentinel',
    'HERA_REDIS_MASTERNAME': '/service/redis/hera/name',
    'HERA_REDIS_DB': '/service/redis/hera/db',
}
