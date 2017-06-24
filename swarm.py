"""A swarm abstraction"""

import hashlib
import re
import time
from threading import Thread

MAX_HASH = int('f' * 40, 16)

# TODO: create a cache table for most of numbers


def swarm_hash(footprint):
    sha1 = hashlib.sha1()
    sha1.update(footprint)
    return int(sha1.hexdigest(), 16)


def hash_range(i, nodes):
    "return the hash space range of Worker i, from a group of nodes"
    delta = MAX_HASH / float(nodes)
    return (i * MAX_HASH / nodes, (i + 1) * MAX_HASH / nodes)


def hash_order(a, b):
    return cmp(a.hash_, b.hash_)


class World(object):
    """Abstraction of world visible for a swarm"""
    def __init__(self):
        self.observers = list()

    def attach(self, obs):
        self.observers.append(obs)

    def push(self, event):
        for obs in self.observers:
            obs.push(event)

    def close(self):
        pass


class Observer(object):
    """World observer"""
    def __init__(self, world, worker):
        self.world = world
        self.worker = worker
        self.rules = list()
        self.regexp = None
        self.world.attach(self)

    def listen(self, rule):
        self.rules.append(rule)
        # build a single regexp that match all rules
        allrules = u'|'.join(['(%s)' % s for s in self.rules])
        print
        print allrules
        self.regexp = re.compile(allrules,
                                 re.DOTALL | re.I | re.UNICODE)

    def detach(self, rule):
        self.rules.remove(rule)

    def push(self, event):
        if self.regexp.match(event.statusline):
            self.worker.queue.append(event)
        else:
            pass




# class Swarm(object):
    # def __init__(self):
        # self.Worker = dict()
        # self.order = list()

    # def add(self, Worker):
        # self.Worker[Worker.hash_] = Worker
        # self.order.append(Worker)
        # self.order.sort(hash_order)

    # def remove(self, Worker):
        # self.Worker.pop(Worker.hash_)

    # def select_attender(self, obj):
        # part = hash_range(0, len(self.Worker))[1]
        # return obj.hash_ / part


class Worker(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):

        Thread.__init__(self, group, target, name, args,
                       kwargs, verbose)

        self.hash_ = swarm_hash(unicode(id(self)))
        self.queue = list()
        self.relax = 0.1
        self.running = False
        self.selfkill__ = 20

    def run(self):
        print "RUN THREAD: %s" % self.hash_
        self.running = True
        while self.running:
            self.step()
            self.debug()

        print "FINISH THREAD: %s" % self.hash_

    def stop(self, timeout=None):
        print "1" * 10
        self.running = False
        self.join(timeout)
        print "2" * 10

    def step(self):
        if self.queue:
            event = self.queue.pop(0)
            print "PROCESSING: ", event
        else:
            print "IDLE: ", self.hash_
            self.idle()

    def idle(self):
        time.sleep(self.relax)
    def debug(self):
        if self.selfkill__:
            self.selfkill__ -=1
            if self.selfkill__ == 0:
                self.running = False
