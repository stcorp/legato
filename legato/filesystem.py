from __future__ import absolute_import, division, print_function
import os
import re
import logging

from watchdog.observers import Observer as FSObserver  # Auto-detect best fs event api according to OS
from watchdog.observers.polling import PollingObserver
from watchdog.events import RegexMatchingEventHandler, FileSystemEventHandler
from watchdog.events import EVENT_TYPE_CREATED, EVENT_TYPE_MODIFIED, EVENT_TYPE_DELETED, EVENT_TYPE_MOVED

import fcntl

from .registry import register
from .run import run_task

logger = logging.getLogger(__name__)


class Observer():
    polling_observer = PollingObserver()
    default_observer = FSObserver()


def start():
    Observer.polling_observer.start()
    Observer.default_observer.start()


def stop():
    Observer.polling_observer.stop()
    Observer.default_observer.stop()


def join():
    Observer.polling_observer.join()
    Observer.default_observer.join()


@register('file', start, stop, join)
def file_trigger(job_name, task_queue, path, events, patterns, **kwargs):
    class Handler(FileSystemEventHandler):
        def __init__(self, basepath, regexes=[r".*"]):
            self._basepath = basepath
            self._regexes = [re.compile(r) for r in regexes]

        @staticmethod
        def run_task(event_path):
            logger.debug('running task %s for %s' % (job_name, event_path))

            environment = os.environ
            environment["FILENAME"] = event_path

            task_queue.put((job_name, dict(environment), kwargs))

        def should_wait_for_unlock(self, path):
            if "unlocked_flock" in events:
                try:
                    logger.debug('trying to open %s (flock)' % path)
                    with open(path, 'r') as lock_file:
                        logger.debug('trying to acquire lock')
                        fcntl.flock(lock_file, fcntl.LOCK_EX)
                        logger.debug('lock acquired')
                except IOError as e:
                    logger.debug('%s is locked (%d)' % (path, e.errno))
                    return True
            if "unlocked_lockf" in events:
                try:
                    logger.debug('trying to open %s (lockf)' % path)
                    with open(path, 'rb+') as lock_file:
                        logger.debug('trying to acquire lock')
                        fcntl.lockf(lock_file, fcntl.LOCK_EX)
                        logger.debug('lock acquired')
                except OSError as e:
                    logger.debug('%s is locked (%d)' % (path, e.errno))
                    return True
            return False

        def on_created(self, event):
            if "create" in events:
                logger.debug('%s was created' % event.src_path)
                relative_path = os.path.relpath(event.src_path, start=self._basepath)
                if any(r.match(relative_path) for r in self._regexes):
                    if self.should_wait_for_unlock(event.src_path):
                        return
                    self.run_task(event.src_path)

        def on_deleted(self, event):
            if "delete" in events:
                logger.debug('%s was deleted' % event.src_path)
                relative_path = os.path.relpath(event.src_path, start=self._basepath)
                if any(r.match(relative_path) for r in self._regexes):
                    self.run_task(event.src_path)

        def on_modified(self, event):
            if "modify" in events:
                logger.debug('%s was modified' % event.src_path)
                relative_path = os.path.relpath(event.src_path, start=self._basepath)
                if any(r.match(relative_path) for r in self._regexes):
                    if self.should_wait_for_unlock(event.src_path):
                        return
                    self.run_task(event.src_path)

        def on_moved(self, event):
            if "movefrom" in events or "moveto" in events:
                logger.debug('%s was moved to %s' % (event.src_path, event.dest_path))
                if "movefrom" in events:
                    relative_path = os.path.relpath(event.src_path, start=self._basepath)
                    if any(r.match(relative_path) for r in self._regexes):
                        self.run_task(event.src_path)
                if "moveto" in events:
                    relative_path = os.path.relpath(event.dest_path, start=self._basepath)
                    if any(r.match(relative_path) for r in self._regexes):
                        self.run_task(event.dest_path)

    operating_system = os.uname()
    if 'Linux' in operating_system:
        with os.popen('stat -f -c %%T -- %s' % path) as pipe:
            file_system = pipe.read()

        # If the file type is ext2/3/4 use i-notify, else use the polling mechanism
        if file_system.startswith('ext'):
            _observer = Observer.default_observer
        else:
            _observer = Observer.polling_observer
    else:
        _observer = Observer.default_observer

    _observer.schedule(Handler(path, regexes=patterns), path, recursive=True)
