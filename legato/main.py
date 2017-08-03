import argparse
import os
import datetime
from daemon import main as daemon
from config import read_configuration_file
from run import run_task


def run(args):
    # Read the configuration
    config_file, _ = read_configuration_file(args.config_file)

    try:
        task = config_file[args.task]
    except:
        raise Exception('Task \'{}\' cannot be found'.format(args.task))

    # Set environment
    environment = os.environ
    if task['type'] == 'time':
        clock = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        environment["DATETIME"] = clock
    elif task['type'] == 'file':
        environment["FILENAME"] = args.filename

    run_task(args.task, env=environment, **task)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("config_file", help="The configuration file")
    parser.add_argument("--verbose", help="Enable debug level logging")
    parser.add_argument("--task", help="Trigger manually a legato task",
                        nargs='?')
    parser.add_argument("--filename", help="Set filename for the action",
                        nargs='?')

    args = parser.parse_args()

    if args.task:
        run(args)
    else:
        daemon(args)


if __name__ == "__main__":
    main()
