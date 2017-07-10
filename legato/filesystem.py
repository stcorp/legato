import os

from watchdog.observers import Observer as FSObserver  # Auto-detect best fs event api according to OS
from watchdog.observers import Observer as PollingObserver
from watchdog.events import *
import fcntl

from legato.registry import register
from legato.run import run_task


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
    class Handler(RegexMatchingEventHandler):
        @staticmethod
        def run_task(event_path):
            run_task(job_name, env={"FILENAME": event_path}, **kwargs)

        def on_any_event(self, event):
            if "unlocked" in events:
                try:
                    file = open(event.src_path, 'r')
                    fcntl.flock(file, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    file.close()
                except IOError:
                    return
            if event.event_type is EVENT_TYPE_CREATED:
                if "create" in events and "modify" not in events:
                    self.run_task(event.src_path)
            if event.event_type is EVENT_TYPE_MODIFIED:
                if "modify" in events:
                    self.run_task(event.src_path)

    file_system = ''
    operating_system = os.uname()
    if 'Linux' in operating_system:
        file_system = os.popen('stat -f -c %%T -- %s' % path).read()

    # If the file type if ext2/3/4 use i-notify, else use the polling mechanism
    if file_system.startswith('ext'):
        _observer = Observer.inotify_observer
    else:
        _observer = Observer.polling_observer

    _observer.schedule(Handler(regexes=patterns), path, recursive=True)
