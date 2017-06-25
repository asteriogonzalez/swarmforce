import os
import yaml

import logging.config
from logging import getLogger, info, debug, error

def setup_logging(path='logging.yaml', level=logging.INFO, env_key='LOG_CFG'):
    path = os.getenv(env_key, path)
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=level)

setup_logging()
