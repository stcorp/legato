from __future__ import absolute_import, division, print_function
import subprocess
import logging
import multiprocessing
import os
from importlib import import_module
from datetime import datetime

logger = logging.getLogger(__name__)


def run_task(job_name, shell=None, cmd=None, python=None, env={}, **kwargs):
    job_reference = job_name
    if "FILENAME" in env:
        job_reference += " for " + env["FILENAME"]

    def run_parallel_task(what, run_shell=False):
        environment = dict(os.environ).update(env)
        try:
            if run_shell is True:
                subprocess.Popen(what, shell=True, executable='/bin/sh', env=environment)
            else:
                what = what.split()
                program = what[0]
                subprocess.Popen(what, shell=False, executable=program, env=environment)
        except (AssertionError, subprocess.CalledProcessError) as e:
            logger.error("failure running %s: %s" % (job_reference, str(e)))

    clock = datetime.now()
    env["DATETIME"] = clock.strftime('%Y-%m-%dT%H:%M:%SZ')
    logger.info("{0} - executing {1}".format(clock.strftime('%Y-%m-%d %H:%M:%SZ'), job_reference))

    if shell is not None:
        run_parallel_task(shell, True)
    if cmd is not None:
        run_parallel_task(cmd, False)
    if python is not None:
        elements = python.split('.')
        module_name = ''
        if len(elements) > 1:
            function_name = elements[-1]
            module_name = '.'.join(elements[:-1])
        else:
            function_name = python

        try:
            module_import = import_module(module_name)
            python_function = getattr(module_import, function_name)
            os.environ.update(env)
            arguments = kwargs.pop('arguments', '')
            def wrapper_function():
                try:
                    python_function(**arguments)
                except Exception as e:
                    logger.error(e)
            process = multiprocessing.Process(target=wrapper_function)
            process.start()
        except Exception as e:
            logger.error(e)
