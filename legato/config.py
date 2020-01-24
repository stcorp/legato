from __future__ import absolute_import, division, print_function
import yaml
import os
import sys


def read_configuration_file(configuration_file):
    list_of_paths = list()
    list_of_paths.append(configuration_file)

    with open(configuration_file, 'r') as fh:
        configuration = yaml.safe_load(fh.read())

    items = {}
    if configuration is not None:
        items.update(configuration.items())

    for name, config in items.items():
        if 'include' in config:
            include = config['include']
            if os.path.isfile(include):
                extra_configuration, extra_paths = read_configuration_file(include)
                if extra_configuration is not None:
                    configuration.update(extra_configuration)
                list_of_paths += extra_paths
            elif os.path.isdir(include):
                list_of_paths += [include]
                for file_in_dir in os.listdir(include):
                    if not file_in_dir[0] == '.':
                        filename = os.path.join(include, file_in_dir)
                        extra_configuration, extra_paths = read_configuration_file(filename)
                        if extra_configuration is not None:
                            configuration.update(extra_configuration)
                        list_of_paths += extra_paths
            else:
                print("include target '%s' does not exist" % include)
                sys.exit(1)

    return configuration, list_of_paths
