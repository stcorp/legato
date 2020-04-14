from __future__ import absolute_import, division, print_function
import argparse
import logging
import os
import sys

from .daemon import main as daemon
from .config import read_configuration_file
from .run import run_task

logger = logging.getLogger(__name__)


def list_tasks(args):
    # Read the configuration
    config_file, _ = read_configuration_file(args.config_file)
    if config_file is None:
        return
    for key in sorted(config_file.keys()):
        if 'include' not in config_file[key]:
            print(key)


def run(args):
    # Read the configuration
    config_file, _ = read_configuration_file(args.config_file)

    try:
        task = config_file[args.task]
    except KeyError:
        raise Exception('Task \'{}\' cannot be found'.format(args.task))

    if 'include' in task:
        raise Exception('Task \'{}\' cannot be run'.format(args.task))

    # Set task-specific environment variables
    environment = {}
    if task['type'] == 'file':
        environment["FILENAME"] = args.filename

    run_task(args.task, env=environment, **task)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("config_file", help="The configuration file", nargs='?')
    parser.add_argument("--verbose", help="Enable debug level logging", action='store_true', default=False)

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--task", help="Trigger manually a legato task")
    group.add_argument("--list", help="List of tasks", action='store_true')

    parser.add_argument("--filename", help="Set filename for the action")

    args = parser.parse_args()

    if args.config_file is None:
        if "LEGATO_CONFIG_PATH" in os.environ:
            args.config_file = os.environ["LEGATO_CONFIG_PATH"]
        else:
            parser.error("no legato configuration file specified")

    try:
        if args.task:
            run(args)
        elif args.list:
            list_tasks(args)
        else:
            daemon(args)
    except Exception as e:
        logger.error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
