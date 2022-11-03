import celery
from celery.utils.log import get_task_logger
from django.core.cache import cache
from redis.client import Redis
from redis.lock import Lock

logger = get_task_logger(__name__)


class SingletonTask(celery.Task):
    lock: Lock = None

    def __call__(self, *args, **kwargs):
        client: Redis = cache._cache.get_client(None, write=True)
        self.lock: Lock = client.lock(self.name)

        if not self.lock.acquire(blocking=False):
            logger.info(f"{self.name}: could not acquire lock")
            return

        try:
            super().__call__(*args, **kwargs)
        except Exception as ex:
            self.lock.release()
            raise ex

        self.lock.release()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        if self.lock:
            self.lock.release()

        print("{0!r} failed: {1!r}".format(task_id, exc))
