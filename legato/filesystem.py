from __future__ import absolute_import, division, print_function
import os
import re
import logging

from watchdog.observers import Observer as FSObserver  # Auto-detect best fs event api according to OS
from watchdog.observers import Observer as PollingObserver
from watchdog.events import RegexMatchingEventHandler, FileSystemEventHandler
from watchdog.events import EVENT_TYPE_CREATED, EVENT_TYPE_MODIFIED, EVENT_TYPE_DELETED, EVENT_TYPE_MOVED

import fcntl

from .registry import register
from .run import run_task


class Observer():
    polling_observer = PollingObserver()
    inotify_observer = FSObserver()


def start():
    Observer.polling_observer.start()
    Observer.inotify_observer.start()


def stop():
    Observer.polling_observer.stop()
    Observer.inotify_observer.stop()


def join():
    Observer.polling_observer.join()
    Observer.inotify_observer.join()


@register('file', start, stop, join)
def file_trigger(job_name, path, events, patterns, **kwargs):
    class Handler(FileSystemEventHandler):
        def __init__(self, basepath, regexes=[r".*"]):
            self._basepath = basepath
            self._regexes = [re.compile(r) for r in regexes]

        @staticmethod
        def run_task(event_path):
            environment = os.environ
            environment["FILENAME"] = event_path
            run_task(job_name, env=environment, **kwargs)

        def on_any_event(self, event):
            try:
                logging.debug('"%s" was %s' % (event.src_path, event.event_type))
                relative_path = os.path.relpath(event.src_path, start=self._basepath)
                if any(r.match(relative_path) for r in self._regexes):
                    if "unlocked" in events:
                        try:
                            lock_file = open(event.src_path, 'r')
                            fcntl.flock(lock_file, fcntl.LOCK_EX)
                            lock_file.close()
                        except IOError:
                            return
                    if event.event_type is EVENT_TYPE_CREATED:
                        if "create" in events and "modify" not in events:
                            self.run_task(event.src_path)
                    if event.event_type is EVENT_TYPE_MODIFIED:
                        if "modify" in events:
                            self.run_task(event.src_path)
            except Exception as e:
                logging.exception(e)
                raise e

    file_system = ''
    operating_system = os.uname()
    if 'Linux' in operating_system:
        file_system = os.popen('stat -f -c %%T -- %s' % path).read()

    # If the file type if ext2/3/4 use i-notify, else use the polling mechanism
    if file_system.startswith('ext'):
        _observer = Observer.inotify_observer
    else:
        _observer = Observer.polling_observer

    _observer.schedule(Handler(path, regexes=patterns), path, recursive=True)
