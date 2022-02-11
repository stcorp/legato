from __future__ import absolute_import, division, print_function
import sys
import os
import logging
from multiprocessing import Process, Queue
import time
import traceback
import signal

from watchdog.observers import Observer
from watchdog.events import *

from . import registry
from .config import read_configuration_file
from .run import run_task

# plugins
from . import timed
from . import filesystem


class MonitorConfigFiles(PatternMatchingEventHandler):
    def __init__(self, observer, *args, **kwargs):
        super(MonitorConfigFiles, self).__init__(*args, **kwargs)
        self.observer = observer

    def on_any_event(self, event):
        self.observer.stop()
        restart()


def run(args, task_queue):
    # Read the configuration
    configuration, list_of_paths = read_configuration_file(args.config_file)
    # Monitor configuration files
    observer = Observer()
    for path_to_monitor in list_of_paths:
        if os.path.isdir(path_to_monitor):
            # create monitor for any change in the directory
            handler = MonitorConfigFiles(observer)
            path = os.path.realpath(path_to_monitor)
        else:
            # create monitor on directory with specific pattern for config file
            handler = MonitorConfigFiles(observer, [os.path.realpath(path_to_monitor)])
            path = os.path.dirname(os.path.realpath(path_to_monitor))
        observer.schedule(handler, path, recursive=False)
    observer.start()

    # parse the config
    if configuration is not None:
        for name, config in configuration.items():
            if 'type' in config:
                type_ = config.pop('type')
                trigger = registry.lookup(type_)
                trigger(name, task_queue, **config)

        # run the config
        registry.start()


def worker_main(task_queue):
    while True:
        job_name, env, kwargs = task_queue.get()
        run_task(job_name, env=env, **kwargs)


def main(args):
    # setup logging
    level = logging.INFO
    if args.verbose:
        level = logging.DEBUG

    # logging
    handler = logging.StreamHandler()
    handler.setLevel(level)
    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)

    # setup worker pool, task queue
    task_queue = Queue()
    for i in range(args.workers):
        process = Process(target=worker_main, args=(task_queue,))
        process.start()

    # run the command
    run(args, task_queue)

    # Prevent main thread to finish
    while True:
        time.sleep(10)


def restart():
    print('Restarting due to change in configuration files')
    registry.stop()
    registry.join()
    executable = os.environ.get('LEGATO', sys.argv[0])
    try:
        os.execvp(executable, sys.argv)
    except Exception:
        traceback.print_exc()
        sys.exit(1)


def shutdown(*args, **kwargs):
    sys.exit()


signal.signal(signal.SIGINT, shutdown)
