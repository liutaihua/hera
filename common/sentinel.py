from celery.backends import BACKEND_ALIASES
from kombu.transport import TRANSPORT_ALIASES
from celery.backends.redis import RedisBackend
from kombu.utils import cached_property
from kombu.transport.redis import Transport, Channel
from redis import Redis
from redis.sentinel import Sentinel

from config.config import TASK_RESULT_STORE_PREFIX_KEY

from common.util import logger

class RedisSentinelBackend(RedisBackend):
    sentinel_timeout = 1
    socket_timeout = 1
    task_keyprefix = TASK_RESULT_STORE_PREFIX_KEY
    group_keyprefix = 'hera-taskset-meta-'
    chord_keyprefix = 'hera-unlock-'
    def __init__(self, sentinels=None, sentinel_timeout=None, socket_timeout=None,
                 min_other_sentinels=0, master_name=None, **kwargs):
        super(RedisSentinelBackend, self).__init__(**kwargs)
        conf = self.app.conf

        def _get(key):
            try:
                return conf['REDIS_SENTINEL_%s' % key]
            except KeyError:
                pass

        self.sentinels = sentinels or _get("SENTINELS")
        self.sentinel_timeout = _get("SENTINEL_TIMEOUT") or self.sentinel_timeout
        self.socket_timeout = _get("SOCKET_TIMEOUT") or self.socket_timeout
        self.min_other_sentinels = min_other_sentinels or _get("MIN_OTHER_SENTINELS")
        self.master_name = master_name or _get("MASTER_NAME")
        self.redis_db = 0 or _get("REDIS_DB")
        logger.debug("redis-sentinel info: sentinels -> {}, redis db -> {}".format(self.sentinels, self.redis_db))


    @cached_property
    def client(self):
        sentinel = Sentinel(self.sentinels,
                            min_other_sentinels=self.min_other_sentinels,
                            socket_timeout=self.sentinel_timeout
                            )
        return sentinel.master_for(self.master_name,
                                   redis_class=Redis,
                                   socket_timeout=self.socket_timeout,
                                   db=self.redis_db)


class SentinelChannel(Channel):
    '''
    this channel use for transport for celery when use redis as the borker
    if only use redis as the result store, this is unused
    '''
    from_transport_options = Channel.from_transport_options + (
        "master_name",
        "sentinels",
        "password",
        "min_other_sentinels",
        "sentinel_timeout",
    )

    @cached_property
    def _sentinel_managed_pool(self):
        sentinel = Sentinel(
            self.sentinels,
            min_other_sentinels=getattr(self, "min_other_sentinels", 0),
            password=getattr(self, "password", None),
            sentinel_kwargs={"socket_timeout": getattr(self, "sentinel_timeout", None)},
        )
        return sentinel.master_for(self.master_name, self.Client,
                                   socket_timeout=self.socket_timeout).connection_pool

    def _get_pool(self):
        return self._sentinel_managed_pool


class RedisSentinelTransport(Transport):
    Channel = SentinelChannel


def register_redis_sentinel(alias="redis-sentinel"):
    BACKEND_ALIASES[alias] = "common.sentinel.RedisSentinelBackend"
    TRANSPORT_ALIASES[alias] = "common.entinel.RedisSentinelTransport"