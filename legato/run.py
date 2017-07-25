import subprocess
import re
import logging
import multiprocessing
import os
from importlib import import_module
from datetime import datetime

logger = logging.getLogger(__name__)


def run_task(job_name, shell=None, cmd=None, python=None, env={}, **kwargs):
    def run_parallel_task(what, run_shell=False):
        try:
            clock = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logger.info("{1} - Executing {0}".format(job_name, clock))
            if run_shell is True:
                subprocess.Popen(what, shell=True, executable='/bin/sh', env=env)
            else:
                what = what.split()
                program = what[0]
                subprocess.Popen(what, shell=False, executable=program, env=env)
        except (AssertionError, subprocess.CalledProcessError) as e:
            logger.error("Failure running %s: %s" % (job_name, str(e)))

    if shell is not None:
        run_parallel_task(shell, True)
    if cmd is not None:
        run_parallel_task(cmd, False)
    if python is not None:
        assert isinstance(python, basestring)
        elements = python.split('.')
        module_name = ''
        function_name = ''
        if len(elements) > 1:
            function_name = elements[-1]
            module_name = '.'.join(elements[:-1])
        else:
            function_name = python
        elements = re.split('[()]', function_name)[:-1]
        arguments = []
        if len(elements) > 1:
            if elements[1] is not '':
                arguments = elements[1].split(',')
        function_name = elements[0]

        module_import = import_module(module_name)
        python_function = getattr(module_import, function_name)
        os.environ = env
        process = multiprocessing.Process(target=python_function, args=arguments)
        process.start()
