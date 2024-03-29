Legato
======
Legato is a daemon that schedules tasks to be performed at specific times or
due to a change in a file or directory. The tasks, which are executed in
separate sub-processes, can be specified as shell scripts, a program or a
call to a Python function.

In music performance and notation, legato [leˈɡaːto] indicates that musical
notes are played or sung smoothly and connected. That is, the player makes a
transition from note to note with no intervening silence.


Installation instructions
~~~~~~~~~~~~~~~~~~~~~~~~~
To be able to use legato, you will need:

- A Unix-based operating system (e.g. Linux).
- Python version 2.7 or higher.
- Dependencies:
  - pyyaml
  - schedule
  - watchdog

Legato is distributed as a source distribution. It can be installed in several
ways, for example, using pip or by invoking setup.py manually.
Installation using setup.py in the default installation location usually
requires super user privileges.

Using pip: ::

  $ pip install legato-1.3.1.tar.gz

Using setup.py: ::

  $ tar zxf legato-1.3.1.tar.gz
  $ cd legato-1.3.1
  $ python setup.py install


Using legato
~~~~~~~~~~~~

Start command
-------------
::

  $ legato configuration_file.yaml

Instead of providing the configuration file as an argument you can also set
the LEGATO_CONFIG_PATH environment variable to point to the file.

Configuration file
------------------
The configuration file follows the YAML format. The first entry is a unique
label to identify the task.

Every entry should include an include directive (to load more configuration
files or directory) or the task configuration.

The task configuration is defined by:

- ``type``: The type of monitoring, it must be ``time`` or ``file``

- ``when``: Applies when the type is set to ``time``. The values can be
  provided in human readable form. For example: "every monday at 17:02" or
  "every 30 seconds"

- ``events``: Applies when the type is set to ``file``. It is a list with file
  events that should be used to trigger on. Supported events are ``modify``,
  ``create``, ``delete``, ``movefrom``, and ``moveto``.
  Optionally it can be complemented with ``unlocked_flock`` or
  ``unlocked_lockf`` (only on Linux and macOS). If an unlocked attribute is
  specified then event triggers for ``create`` and ``modify`` will only happen
  once the file is unlocked (using flock or fcntl respectively). Write
  permission on the file is needed to use ``unlocked_lockf``

- ``path``: Applies when the type is set to ``file``. It describes the
  directory to monitor

- ``patterns``: Applies when the type is set to ``file``. It describes the
  pattern that will trigger the action

- ``shell``:  The shell command to be run

- ``cmd``:  The external program with arguments to be executed

- ``python``:  The Python function to be called, in the form of a full
  module path. An optional sub-attribute ``arguments`` contains arguments to
  be passed to the function.

In case of ``file`` monitoring, the respective file name for an event is passed
to the external command or Python function via an environment variable named
``FILENAME``.


Example configuration file
--------------------------
::

   include_file:
     include: extra_config_file.yaml

   include_dir:
     include: extra_config_dir/

   echo_something:
     type: time
     when: every monday at 17:02
     shell: |
       echo "Something"

   echo_something_else:
     type: time
     when: every 1 minutes
     shell: |
       bar='foo'
       echo "Something else: $bar"

   echo_timestamp_trigger:
     type: time
     when: every 3 seconds
     shell: |
       echo Timestamp trigger $DATETIME

   echo_filesystem:
     type: file
     events: ["modify", "create", "movefrom"]
     path: /tmp/test/
     patterns:
       - '.*\.(json|py)'
     shell: |
       echo "$FILENAME"

   echo_networkshare:
     type: file
     events: ["modify", "create"]
     path: /mnt/network_share/
     patterns:
       - '.*\.(json|py)'
     shell: |
       echo "$FILENAME"

   echo_cmd:
     type: time
     when: every 35 seconds
     cmd: /bin/ls ..

   echo_python:
     type: time
     when: every 3 seconds
     python: legato.demo.echo
     arguments:
        text_one: 'Hello'
        text_two: 'World'

   echo_helloworld_python:
     type: time
     when: every 5 seconds
     python: legato.demo.echo_helloworld


Command-line arguments
----------------------
Positional arguments:

- ``config_file``: The configuration file.

Optional arguments:

- ``task``: Manually trigger the specified task.
- ``filename`` Specify file name when using the ``task`` argument with ``file``
  monitoring.
- ``list``: List all tasks.
- ``workers`` Number of worker processes (default 1).
