"""Test swarm abtraction module"""

import time
import hashlib
import pytest
from swarmforce.swarm import World, Observer, Worker, \
     MAX_HASH, hash_range
from swarmforce.http import Event


@pytest.fixture(scope="module")
def world():
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

    worker = Worker()
    observer = Observer(world, worker)

    observer.listen('NEW|UPDATE /inbox')
    observer.listen('UPDATE /done')
    observer.listen('.* /workers')

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

    assert len(worker.queue) == 2

    worker.start()

    for _ in range(10):
        if worker.queue:
            time.sleep(0.1)
        else:
            break

    worker.stop()

    assert len(worker.queue) == 0
    a = 2
    print "END "* 10


# End
