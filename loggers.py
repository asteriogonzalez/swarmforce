import os
import yaml

import logging.config
from logging import getLogger, info, debug, error

log_configfile = None


def _setup_logging(path='logging.yaml', level=logging.INFO, env_key='LOG_CFG'):
    global log_configfile

    path = os.path.abspath(path)
    print "=" * 50
    print ">> setup_logging:", path

    path = os.getenv(env_key, path)
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())

        logging.config.dictConfig(config)
        log_configfile = os.path.abspath(path)

    else:
        logging.basicConfig(level=level)

    print "<< setup_logging:", log_configfile
    return log_configfile


def setup_logging(path='logging.yaml', level=logging.INFO, env_key='LOG_CFG'):
    name = os.path.basename(path)
    home = os.path.abspath(os.path.dirname(path))
    for root, _, files in os.walk(home):
        if name in files:
            return _setup_logging(os.path.join(root, name),
                                  level, env_key)

    raise RuntimeError("Can not find %s config file in %s tree" %
                       (path, home))

# setup_logging()
