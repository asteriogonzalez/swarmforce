"""A swarm abstraction"""

import hashlib
import re
import time
from threading import Thread
from swarmforce.loggers import getLogger
from swarmforce.http import Request, Response, \
     X_CLIENT, X_REQ_ID
from swarmforce.misc import hasher, until

log = getLogger('swarmforce')


MAX_HASH = int('f' * 40, 16)

# TODO: create a cache table for most of numbers
# DONE: Use DEFINES for http headers
# DONE: callback requests based on regexp
# TODO: trace requests / responses tree across hosts
# TODO: asyncronous complex tree algoritms (data flow process)
# TODO: draw request complex executions
# DONE: remove threading dependences and use Reactor or evenlet


RUNNING = 3
PAUSED = 2
SWITCHING = 1
STOPPED = 0


def hash_range(i, nodes):
    "return the hash space range of Worker i, from a group of nodes"
    delta = MAX_HASH / float(nodes)
    return (i * MAX_HASH / nodes, (i + 1) * MAX_HASH / nodes)


def hash_order(a, b):
    "sort function for comparing to swarm objects"
    return cmp(a.hash_, b.hash_)


class World(Thread):
    """Abstraction of world visible for a swarm"""
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):

        Thread.__init__(self, group, target, name, args,
                        kwargs, verbose)

        self.workers = dict()
        self.running = STOPPED
        self.relax = 0.1

        self.queue = list()
        self.pending = dict()


        log.info('New World at: %s', self)

    def push(self, event):
        "broadcast an event to all workers trought their observers"
        if isinstance(event, Request):
            event.hash()
            self.pending[event.key] = event

        if event.sane():
            self.queue.append(event)
        else:
            log.error('MALFORMED event: %s', event.dump())


    def new(self, klass, *args, **kw):
        """Create a pair of worker / observer, attach them
        and set worker to run."""

        worker = klass(*args, **kw)
        self.workers[worker.hash_] = worker
        worker.world = self
        return worker

    def run(self):
        log.info("RUN: %s", self)
        end = time.time() + 60
        self.running = RUNNING
        while self.running > STOPPED:
            self.step()
            if time.time() > end:
                break

        log.info("FINISH: %s", self)

    def step(self):
        """Process the next event if worker is in RUNNING mode
        or performs a idle action when queue is empty"""
        if self.running > PAUSED:
            if self.queue:
                event = self.queue.pop(0)
                if isinstance(event, Request):
                    self.dispatch_request(event)
                    if event.response:
                        # log.warn('sending response: %s',
                        # event.response.dump())
                        self.push(event.response)
                else:  # Response
                    self.dispatch_response(event)
            else:
                self.idle()
        else:
            log.info('%s is PAUSED', self)
            time.sleep(0.2)

    def idle(self):
        "Performs an idle task. Should be overrrided."
        time.sleep(self.relax)

    def set(self, running):
        """Set the running state of worker:
        RUNNING: process event normally
        SWITHING: blocks incoming events while process existin in queue
        PAUSE: do not process events, but new one area allowed
        STOPPED: worker is done
        """
        self.running = running

    def stop(self, timeout=5):
        "Stops the worker while trying to flush the queue"
        if self.running != STOPPED:
            # log.info('Stopping %s', self)
            self.running = SWITCHING
            end = time.time() + timeout
            while self.queue and time.time() < end:
                time.sleep(0.1)

            self.running = STOPPED
            self.join(timeout)
            log.info('Stopped %s', self)
        else:
            log.info('Already Stopped %s', self)


    def dispatch_request(self, event):
        "Process the event. Must be overriden."
        for worker in self.workers.values():
            worker.dispatch_request(event)

    def dispatch_response(self, event):
        "Process a response. Must be overriden."

        request = self.pending.pop(event[X_REQ_ID], None)
        if request is None:
            log.warn('%s Can not find associated resquest %s',
                     self, event.dump())
            log.warn(self.pending.keys())
        else:
            log.debug('%s Found associated request: %s',
                      self, event[X_REQ_ID])

            event.request = request
            worker = self.workers.get(event[X_CLIENT])
            worker.dispatch_response(event)

class Worker(object):
    """A treaded worker that process request and responses from a queue
    managed by an observer which connect the worker to the world.
    """
    def __init__(self):

        self.hash_ = hasher(unicode(id(self)))
        self.world = None

        self.rules = list()
        self.regexp = re.compile('invalid^.{1000,}$')

        self.response_callbacks = list()

        log.info('New Worker at: %s', self)

    def dispatch_request(self, event):
        "Process the event. Must be overriden."
        log.warn('Must be overriden: %s', event.dump())

    def dispatch_response(self, event):
        "Process a response. Must be overriden."
        log.warn('ATTENDIND RESPONSE: %s from %s', event, event.request)
        code = event.code
        for regxp, func in self.response_callbacks:
            if regxp.match(code):
                log.warn('--> %s', func)
                func(event)

    def send(self, event):
        "Send an event to the world"
        self.world.push(event)

    def new_request(self, **kw):
        "Create a this-worker specific Request"
        req = Request(**kw)
        req[X_CLIENT] = self.hash_
        return req

    # observer part
    def listen(self, rule):
        """Append a new listen rule to the existing and
        compiles a full reg expression that match any of the rules.
        """
        self.rules.append(rule)
        # build a single regexp that match all rules
        allrules = u'|'.join(['(%s)' % s for s in self.rules])
        self.regexp = re.compile(allrules,
                                 re.DOTALL | re.I | re.UNICODE)

    def unlisten(self, rule):
        "remove a rule and rebuild the full regexp"
        self.rules.remove(rule)
        # build a single regexp that match all rules
        allrules = u'|'.join(['(%s)' % s for s in self.rules])
        self.regexp = re.compile(allrules,
                                 re.DOTALL | re.I | re.UNICODE)

    # response handlers
    def add_response_handler(self, regexp, func):
        self.response_callbacks.append(
            (re.compile(regexp, re.I | re.DOTALL), func))

    def response_OK(self, respone, request):
        pass

    def response_ERROR(self, respone, request):
        pass



# End
