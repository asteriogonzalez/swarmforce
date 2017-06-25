"""Test swarm abtraction module"""
import sys
import time
import hashlib
import pytest
from swarmforce.swarm import World, Observer, Worker, \
     MAX_HASH, hash_range, RUNNING, PAUSED
from swarmforce.http import Event

from swarmforce.loggers import getLogger

log = getLogger('swarmforce')

def until(condition, timeout=5):
    "Wait until condition is true"
    frame = sys._getframe().f_back
    end = time.time() + timeout
    while time.time() < end:
        result = eval(condition, frame.f_globals, frame.f_locals)
        log.info('(%s) ==> %s', condition, result)
        if result:
            break
        time.sleep(0.1)


@pytest.fixture(scope="module")
def world():
    "Provide a world that is not shared across all tests"
    world = World()

    yield world
    world.close()


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

    worker.observer.listen('NEW|UPDATE /inbox')
    worker.observer.listen('UPDATE /done')
    worker.observer.listen('.* /workers')

    worker.set(RUNNING)

    # match
    event = Event()
    event.method = 'NEW'
    event.path = '/inbox/123'
    event.body = 'Hello World'
    world.push(event)

    # match
    event = Event()
    event.method = 'UPDATE'
    event.path = '/done/123'
    event.body = 'Hello World'
    world.push(event)

    # don't match
    event = Event()
    event.method = 'DELETE'
    event.path = '/done/123'
    event.body = 'Hello World'
    world.push(event)

    worker.set(RUNNING)
    assert len(worker.queue) == 2
    until('len(worker.queue) == 0')
    assert len(worker.queue) == 0


# End
