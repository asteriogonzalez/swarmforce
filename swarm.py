"""A swarm abstraction"""

import hashlib
import re
import time
from threading import Thread
from swarmforce.loggers import getLogger

log = getLogger('swarmforce')


MAX_HASH = int('f' * 40, 16)

# TODO: create a cache table for most of numbers
# TODO: callback requests based on regexp
# TODO: trace requests / responses tree across hosts
# TODO: asyncronous complex tree algoritms (data flow process)
# TODO: draw request complex executions

RUNNING = 3
PAUSED = 2
SWITCHING = 1
STOPPED = 0

def swarm_hash(footprint):
    "hasher used for all objects in project"
    sha1 = hashlib.sha1()
    sha1.update(footprint)
    return int(sha1.hexdigest(), 16)


def hash_range(i, nodes):
    "return the hash space range of Worker i, from a group of nodes"
    delta = MAX_HASH / float(nodes)
    return (i * MAX_HASH / nodes, (i + 1) * MAX_HASH / nodes)


def hash_order(a, b):
    "sort function for comparing to swarm objects"
    return cmp(a.hash_, b.hash_)


class World(object):
    """Abstraction of world visible for a swarm"""
    def __init__(self):
        self.observers = list()
        self.workers = dict()
        log.info('New World at: %s', self)

    def attach(self, obs):
        "attach an observer to this world"
        self.observers.append(obs)

    def push(self, event):
        "broadcast an event to all workers trought their observers"
        for obs in self.observers:
            obs.attend(event)

    def close(self):
        "try to close all known workers"
        for worker in self.workers.values():
            worker.stop()

    def new(self, klass, *args, **kw):
        """Create a pair of worker / observer, attach them
        and set worker to run."""

        worker = klass(*args, **kw)
        observer = Observer(self, worker)
        worker.start()
        self.workers[worker.hash_] = worker
        return worker


class Observer(object):
    """World observer"""
    def __init__(self, world, worker):
        self.world = world
        self.worker = worker
        self.rules = list()
        self.regexp = re.compile('invalid^.{1000,}$')
        self.queue = list()
        self.pending = dict()

        self.world.attach(self)
        self.worker.attach(self)

    def listen(self, rule):
        """Append a new listen rule to the existing and
        compiles a full reg expression that match any of the rules.
        """
        self.rules.append(rule)
        # build a single regexp that match all rules
        allrules = u'|'.join(['(%s)' % s for s in self.rules])
        self.regexp = re.compile(allrules,
                                 re.DOTALL | re.I | re.UNICODE)

    def detach(self, rule):
        "remove a rule and rebuild the full regexp"
        self.rules.remove(rule)
        # build a single regexp that match all rules
        allrules = u'|'.join(['(%s)' % s for s in self.rules])
        self.regexp = re.compile(allrules,
                                 re.DOTALL | re.I | re.UNICODE)

    def attend(self, event):
        "Analyze an event to determine if its worker must process or not."
        if self.regexp.match(event.statusline):
            if self.worker.running > SWITCHING:
                self.queue.append(event)
            else:
                log.info('SKIPING event %s', event)
        else:
            pass

    def send(self, event):
        "Send an event to the world"
        self.pending[event.key] = event
        self.observer.world.push(event)


class Worker(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):

        Thread.__init__(self, group, target, name, args,
                        kwargs, verbose)

        self.hash_ = swarm_hash(unicode(id(self)))
        self.observer = None
        self.queue = None # shared with observer
        self.relax = 0.1
        self.running = STOPPED

        log.info('New Worker at: %s', self)

    def run(self):
        log.info("RUN: %s", self)
        self.running = RUNNING
        while self.running > STOPPED:
            self.step()

        log.info("FINISH: %s", self)

    def stop(self, timeout=5):
        "Stops the worker while trying to flush the queue"
        if self.running != STOPPED:
            log.info('Stopping %s', self)
            self.running = SWITCHING
            t1 = time.time() + timeout
            while self.queue and time.time() < t1:
                time.sleep(0.1)

            self.running = STOPPED
            self.join(timeout)
            log.info('Stopped %s', self)
        else:
            log.info('Already Stopped %s', self)

    def step(self):
        """Process the next event if worker is in RUNNING mode
        or performs a idle action when queue is empty"""
        if self.running > PAUSED:
            if self.queue:
                event = self.queue.pop(0)
                self.dispatch(event)
            else:
                self.idle()

    def dispatch(self, event):
        "Process the event. Must be override."
        # print "PROCESSING: ", event
        pass

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

    def send(self, event):
        "Send an event to the world"
        self.observer.send(event)

    def attach(self, observer):
        "Attach the observer to inteact with the world"
        self.observer = observer
        self.queue = observer.queue

# End
