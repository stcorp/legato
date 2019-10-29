from __future__ import absolute_import, division, print_function
import sys
import os
import logging
import time
import signal

from watchdog.observers import Observer
from watchdog.events import *

from . import registry
from .config import read_configuration_file

# plugins
from . import timed
from . import filesystem


class MonitorConfigFiles(PatternMatchingEventHandler):
    def on_any_event(self, event):
        restart()


def run(args):
    # Read the configuration
    configuration, list_of_paths = read_configuration_file(args.config_file)
    # Monitor configuration files
    observer = Observer()
    for path_to_monitor in list_of_paths:
        if os.path.isdir(path_to_monitor):
            # create monitor for any change in the directory
            handler = MonitorConfigFiles()
            path = os.path.realpath(path_to_monitor)
        else:
            # create monitor on directory with specific pattern for config file
            handler = MonitorConfigFiles([os.path.realpath(path_to_monitor)])
            path = os.path.dirname(os.path.realpath(path_to_monitor))
        observer.schedule(handler, path, recursive=False)
    observer.start()

    # parse the config
    if configuration is not None:
        for name, config in configuration.items():
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
    executable = os.environ.get('LEGATO', sys.argv[0])
    try:
        os.execvp(executable, sys.argv)
    except Exception as e:
        print(e)
        sys.exit(1)


def shutdown(*args, **kwargs):
    sys.exit()

signal.signal(signal.SIGINT, shutdown)

