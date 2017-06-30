"""Test swarm abtraction module"""
import time
import os
import hashlib
import subprocess
import pytest

from swarmforce.misc import expath
from swarmforce.swarm import World, Worker, \
     MAX_HASH, hash_range, RUNNING, PAUSED
from swarmforce.http import Event, Request, Response, \
     X_TIME, X_REMAIN_EXECUTIONS
from swarmforce.misc import until
from swarmforce.tests.demo_workers import Boss, EvalWorker
from swarmforce.loggers import getLogger, setup_logging

from loganalizer.main import get_files_fmt, MultiParser


log_configfile = setup_logging('test_logging.yaml')
log = getLogger('swarmforce')


def test_hash_reallocation():
    "Test hash reallocation space for automatic queue assignment"

    sha1 = hashlib.sha1()
    sha1.update(u'12')
    hash_ = sha1.hexdigest()
    max_ = 'f' * len(hash_)
    max_ = int(max_, 16)

    assert max_ == MAX_HASH

    for i in range(1, 100):
        assert hash_range(0, i)[0] == 0
        assert hash_range(i - 1, i)[1] == MAX_HASH


def test_swarm_init(world):
    "Simple test for creating a worker that listen to some events"

    worker = world.new(Worker)

    worker.listen('NEW|UPDATE /inbox')
    worker.listen('UPDATE /done')
    worker.listen('.* /workers')

    world.set(PAUSED)

    # match
    event = Request()
    event.method = 'NEW'
    event.path = '/inbox/123'
    event.body = 'Hello World'
    world.push(event)

    # match
    event = Request()
    event.method = 'UPDATE'
    event.path = '/done/123'
    event.body = 'Hello World'
    world.push(event)

    # don't match
    event = Request()
    event.method = 'DELETE'
    event.path = '/done/123'
    event.body = 'Hello World'
    world.push(event)

    assert len(world.queue) == 3
    world.set(RUNNING)
    until('len(world.queue) == 0')
    assert len(world.queue) == 0


def test_swarm_calc(world):
    "Simple client / server pattern"

    client = world.new(Boss)
    worker = world.new(EvalWorker)
    worker.listen('DO /inbox/eval')

    # match
    req = client.new_request()
    req.method = 'DO'
    req.path = '/inbox/eval'
    req.body = '1 + 2'
    client.send(req)

    until("client.response == '3'")


def test_deferred_requests(world):
    """test timeout and deferred responses"""
    client = world.new(Boss)
    worker = world.new(EvalWorker)
    worker.listen('DO /inbox/eval')

    now = time.time()
    req = client.new_request()
    req.method = 'DO'
    req.path = '/inbox/eval'
    req.body = '1 + 2'
    req[X_TIME] = now + 1
    client.send(req)

    assert not world.queue

    until("client.response == '3'")


def test_remain_executions(world, clean_logs):
    """test remain executions for a requests"""

    global log_configfile

    client = world.new(Boss)
    worker = world.new(EvalWorker)
    worker.listen('DO /inbox/eval')

    N = 3
    req = client.new_request()
    req.method = 'DO'
    req.path = '/inbox/eval'
    req.body = '1 + 2'
    req[X_REMAIN_EXECUTIONS] = N
    client.send(req)

    until("client.hits == N")

    #
    # Checking N hits directly from logs analysis
    formatters = get_files_fmt(log_configfile)

    parser = MultiParser(formatters, database='logs.sqlite')
    #parser = MultiParser(formatters)
    parser.parse_all()

    info = parser.assert_on(funcname='answer', message='Creat.*response')
    # assert len(info) == N

    foo = 122



# End
