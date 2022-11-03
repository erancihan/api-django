from typing import Dict, Any

import celery
from celery.utils.log import get_task_logger
from django.core.cache import cache
from redis.client import Redis
from redis.lock import Lock

from server.celery import app

logger = get_task_logger(__name__)


class DebounceTask(celery.Task):
    client: Redis

    timeout = None

    wait = 0
    leading = False
    trailing = False
    reacquire = False

    def __call__(self, *args, **kwargs):
        self.client: Redis = cache._cache.get_client(None, write=True)
        self.timeout = self.time_limit

        if self.reacquire:
            self._cancel_previous_task()

            # in first run, there is no LOCK, acquire it
            if not self.lock_locked():
                if not self.lock_acquire():
                    # could... not acquire it????
                    logger.warning(f"{self.name}: could not acquire lock")
                    return
        else:
            if not self.lock_acquire():
                return

        try:
            # if trailing, call happens on the trailing edge,
            #   calls before the function process will be dropped
            # ...||||#...
            if self.trailing and self.wait > 0:
                time.sleep(self.wait)

            super().__call__(*args, **kwargs)

            # if leading, call happens on the leading edge.
            #   calls after the function invoked will be dropped.
            # ...#||||...
            if self.leading and self.wait > 0:
                time.sleep(self.wait)

        except Exception as ex:
            self.lock_release()
            raise ex

        self.lock_release()

    def lock_locked(self) -> bool:
        return self.client.get(self.name) is not None

    def lock_acquire(self) -> bool:
        if self.client.set(self.name, self.name, nx=True, px=self.timeout):
            return True
        return False

    def lock_reacquire(self) -> bool:
        if not self.timeout:
            return
        self.client.expire(self.name, int(self.timeout * 1000))

    def lock_release(self):
        self.client.delete(self.name)

    def _cancel_previous_task(self):
        # cancel previous task with same name
        # if there is a task with same name, then the lock should already be in place
        inspect = app.control.inspect()
        actives: Dict[string, Any] = inspect.active()

        for _, active_tasks in actives.items():
            for task in active_tasks:
                if task["name"] != self.name:
                    # skip other tasks
                    continue
                if task["id"] == self.request.id:
                    # skip self
                    continue

                # found an active call with same name
                # - reacquire it's lock
                self.lock_reacquire()

                # - revoke task
                app.control.revoke(task["id"], terminate=True)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        self.lock_release()

        print("{0!r} failed: {1!r}".format(task_id, exc))
