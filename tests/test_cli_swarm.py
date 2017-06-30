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
from swarmforce.loggers import getLogger

log = getLogger('swarmforce')



def test_connect_swarm(world):
    """# TODO: USER HISTORY 'connect to swarm'
    # 1. from console, launch swarm node
    # 2. view swarm status
    # 3. launch some calc workers that stay idle
    # 4. create 100 requets and let the swarm process them
    # 5. query for stats
"""
    args = ['sf.py']
    cwd = expath(os.path.dirname(__file__), '../cli')
    log.warn(cwd)

    cmd = './sf.py'

    log.info('Launching ... %s' % cmd)

    for i in xrange(2):
        p = subprocess.Popen(cmd, cwd=cwd)

        log.info('Waiting ...')
    p.wait()

    log.info('Done ...')
    foo = 1233



# End
