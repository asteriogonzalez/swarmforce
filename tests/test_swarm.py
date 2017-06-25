"""Test swarm abtraction module"""
import time
import hashlib
import pytest
from swarmforce.swarm import World, Worker, \
     MAX_HASH, hash_range, RUNNING, PAUSED
from swarmforce.http import Event, Request, Response
from swarmforce.misc import until
from swarmforce.loggers import getLogger

log = getLogger('swarmforce')


class Boss(Worker):
    "A client agent"

    def __init__(self):
        Worker.__init__(self)
        self.add_response_handler('2\d\d$', self.response_OK)

    def response_OK(self, response):
        request = response.request
        log.info('%s ---> %s', request.body, response.body)
        self.response = response.body


class Calc(Worker):
    "A server agent"


    def dispatch_request(self, event):
        result = eval(event.body)
        answer = event.answer()
        answer.body = unicode(result)
        log.info(answer.dump())


@pytest.fixture(scope="function")
def world(request):
    "Provide a world that is not shared across all tests"
    world = World()
    world.start()

    def fin():
        world.stop()

    request.addfinalizer(fin)
    return world


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
    worker = world.new(Calc)
    worker.listen('DO /inbox/calc')

    # match
    req = client.new_request()
    req.method = 'DO'
    req.path = '/inbox/calc'
    req.body = '1 + 2'
    client.send(req)

    until("client.response == '3'")

    log.warn(client.response)

    foo = 123


# End
