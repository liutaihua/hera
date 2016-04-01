FAILED_TASK_RETRY_MAX_TIMES = 3

# if enable, will substitute the celery strategy with the common/strategy.py
ENABLE_CUSTOMER_STRATEGY = True

# maximum number of revokes to keep in memory.
REVOKES_MAX = 100
REVOKE_EXPIRES = 0

TASK_RESULT_STORE_PREFIX_KEY = 'hera-task-meta-'

# if set the etcd, will get this setting value from etcd
# or you can set them manual:
CELERY_CONCURRENCY = 5000
RABBITMQ = 'amqp://celery:celery@127.0.0.1:5672/celery'
HERA_REDIS_SENTINEL = '127.0.0.1:26379'
HERA_REDIS_MASTERNAME = 'my_db'
HERA_REDIS_DB = '0'

#ETCD_HOST = '127.0.0.1'
#ETCD_PORT = 2379
#hera_etcd_settings = {
#    'CELERY_CONCURRENCY': '/config/hera/celery_concurrency',
#    'RABBITMQ': '/service/rabbitmq/hera',
#    'HERA_REDIS_SENTINEL': '/service/redis/hera/sentinel',
#    'HERA_REDIS_MASTERNAME': '/service/redis/hera/name',
#    'HERA_REDIS_DB': '/service/redis/hera/db',
#}
