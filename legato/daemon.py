from __future__ import absolute_import, print_function
import sys
import os
import logging
import signal
from watchdog.observers import Observer
from watchdog.events import *

from legato import registry
from legato.config import read_configuration_file
import time

# plugins
import legato.timed
import legato.filesystem


class MonitorConfigFiles(RegexMatchingEventHandler):
    def on_any_event(self, event):
        if event.event_type is EVENT_TYPE_CREATED or event.event_type is EVENT_TYPE_MODIFIED:
            restart()


def run(args):
    # Read the configuration
    config_file, list_of_files = read_configuration_file(args.config_file)
    # Monitor configuration files
    observer = Observer()
    for file_to_monitor in list_of_files:
        handler = MonitorConfigFiles(os.path.realpath(file_to_monitor))
        path = os.path.dirname(os.path.realpath(file_to_monitor))
        observer.schedule(handler, path, recursive=False)
    observer.start()

    # parse the config
    if config_file is not None:
        for name, config in config_file.items():
            if 'type' in config:
                trigger = registry.lookup(config['type'])
                trigger(name, **config)

        # run the config
        registry.start()


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

    # run the command
    run(args)

    # Prevent main thread to finish
    while True:
        time.sleep(10)


def restart():
    print('Restarting due to change in configuration files')
    registry.stop()
    registry.join()
    try:
        os.execvp("legato", sys.argv)
    except Exception as e:
        print(e)
        sys.exit(1)


def shutdown(*args, **kwargs):
    sys.exit()

signal.signal(signal.SIGINT, shutdown)

