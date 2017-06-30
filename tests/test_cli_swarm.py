"""Test swarm abtraction module"""
import time
import os
import hashlib
import pytest
import subprocess

from swarmforce.misc import expath
from swarmforce.swarm import World, Worker, \
     MAX_HASH, hash_range, RUNNING, PAUSED
from swarmforce.http import Event, Request, Response, \
     X_TIME, X_REMAIN_EXECUTIONS
from swarmforce.misc import until
from demo_workers import Boss, EvalWorker
from swarmforce.loggers import getLogger, setup_logging

from loganalizer.main import get_files_fmt, MultiParser


# os.environ['LOGGING_CFG'] = expath('test_logging.yaml')
log_configfile = setup_logging('test_logging.yaml')
log = getLogger('swarmforce')


def test_connect_swarm(clean_logs,  world, log_now):
    """# TODO: USER HISTORY 'connect to swarm'
    # 1. from console, launch swarm node
    # 2. view swarm status
    # 3. launch some calc workers that stay idle
    # 4. create 100 requets and let the swarm process them
    # 5. query for stats
"""

    global log_configfile
    print "log_now=", log_now

    args = ['sf.py']
    cwd = expath(os.path.dirname(__file__), '../cli')
    log.warn(cwd)

    cmd = './sf.py'

    log.info('Launching ... %s', cmd)

    for i in xrange(2):
        p = subprocess.Popen(cmd, cwd=cwd, env=os.environ)
        log.info("SUBPROCESS PID = %s", p.pid)
        # p = subprocess.Popen(cmd, cwd=cwd)

        log.info('Waiting for subprocess to end ...')
    p.wait()

    #
    # Checking N hits directly from logs analysis
    formatters = get_files_fmt(log_configfile)

    parser = MultiParser(formatters, database='logs.sqlite')
    # parser = MultiParser(formatters)
    parser.parse_all()

    # info = parser.assert_on(funcname='answer', message='Creat.*response')
    # assert len(info) == N

    log.info('Done ...')
    foo = 1


# End
