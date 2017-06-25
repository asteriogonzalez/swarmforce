import os
import hashlib

import sys
import time
from random import choice, randint
alphabet='ABCDEFGHIJKLMNOPQRSTUVWYZ0123456789_'

def random_token(length=10, minimum=3):
    token = []
    for i in range(minimum, randint(minimum + 1, length + 1)):
        token.append(choice(alphabet))

    return ''.join(token)

def random_path(length=10, minimum=3, sep='/', lead=True):
    if lead:
        path = ['']
    else:
        path = []

    for i in range(minimum, randint(minimum + 1, length + 1)):
        path.append(random_token())

    return sep.join(path)

def hasher(footprint):
    "hasher used for all objects in project"
    sha1 = hashlib.sha1()
    sha1.update(footprint)
    # return int(sha1.hexdigest(), 16)
    return sha1.hexdigest()

def until(condition, timeout=5):
    "Wait until condition is true"
    frame = sys._getframe().f_back
    end = time.time() + timeout
    while time.time() < end:
        result = eval(condition, frame.f_globals, frame.f_locals)
        if result:
            break
        time.sleep(0.1)
    else:
        raise RuntimeError(
            'Timeout (%s) while waiting for condition %s' % \
        (timeout, condition))
