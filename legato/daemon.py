from __future__ import absolute_import, print_function
import sys
import os
import argparse
import logging
import signal
from watchdog.observers import Observer
from watchdog.events import *

import yaml
from legato import registry
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


def read_configuration_file(configuration_file):
    list_of_files = list()
    list_of_files.append(configuration_file)

    with open(configuration_file, 'r') as fh:
        configuration = yaml.load(fh.read())

    items = {}
    if configuration is not None:
        items.update(configuration.items())

    for name, config in items.items():
        if 'include' in config:
            include = config['include']
            if os.path.isfile(include):
                extra_configuration, extra_files = read_configuration_file(include)
                if extra_configuration is not None:
                    configuration.update(extra_configuration)
                list_of_files += extra_files
            elif os.path.isdir(include):
                for file_in_dir in os.listdir(include):
                    filename = os.path.join(include, file_in_dir)
                    extra_configuration, extra_files = read_configuration_file(filename)
                    if extra_configuration is not None:
                        configuration.update(extra_configuration)
                    list_of_files += extra_files
            else:
                raise IOError

    return configuration, list_of_files


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("config_file", help="The configuration file")
    parser.add_argument("--verbose", help="Enable debug level logging")

    args = parser.parse_args()

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
    os.execvp("legato", sys.argv)


def shutdown(*args, **kwargs):
    sys.exit()

signal.signal(signal.SIGINT, shutdown)

if __name__ == "__main__":
    main()
