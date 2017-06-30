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

        logging.config.dictConfig(config)
        log_configfile = os.path.abspath(path)

    else:
        logging.basicConfig(level=level)

    print "=" * 10
    print "Used log_configfile = ", log_configfile
    print "=" * 10

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


# Main default setup
setup_logging()
