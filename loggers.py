import os
import yaml

import logging
import logging.config
from logging import getLogger, info, debug, error

log_configfile = None

from pprint import pprint

def setup_logging(path='logging.yaml', level=logging.INFO, env_key='LOGGING_CFG'):
    global log_configfile

    path = os.path.abspath(path)

    path = os.getenv(env_key, path)
    if os.path.exists(path):
        with open(path, 'rt') as f:
            content = f.read()
            content = os.path.expandvars(content)

            config = yaml.safe_load(content)

        create_parent_folders(config)
        logging.config.dictConfig(config)
        log_configfile = os.path.abspath(path)

    else:
        logging.basicConfig(level=level)

    # print "=" * 10
    # print "Used log_configfile = ", log_configfile
    # print "=" * 10

    return log_configfile


def hide_setup_logging(path='logging.yaml', level=logging.INFO, env_key='LOGGING_CFG'):
    name = os.path.basename(path)
    home = os.path.abspath(os.path.dirname(path))
    for root, _, files in os.walk(home):
        if name in files:
            return _setup_logging(os.path.join(root, name),
                                  level, env_key)

    raise RuntimeError("Can not find '%s' under '%s' tree" %
                       (path, home))


def flush():
    for handler in logging._handlers.values():
        # print "FLUSHING", handler
        handler.flush()



def create_parent_folders(config):
    for name, handler in config['handlers'].items():
        filename = handler.get('filename')
        if filename:
            parent = os.path.dirname(filename)
            if not os.path.exists(parent):
                os.makedirs(parent)

def reset_logs():
    for handler in logging._handlers.values():
        if isinstance(handler, logging.FileHandler):
            file(handler.baseFilename, 'w').write('')


# Main default setup
setup_logging()
