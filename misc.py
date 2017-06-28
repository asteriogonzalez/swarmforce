"""Some convenience functions"""

import os
import hashlib

import sys
import time
from random import choice, randint
alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWYZ0123456789_'

# -----------------------------------------
# Random generator data
# -----------------------------------------
def random_token(length=10, minimum=3):
    "Generate a random token"
    token = []
    for i in range(minimum, randint(minimum + 1, length + 1)):
        token.append(choice(alphabet))

    return ''.join(token)

def random_path(length=10, minimum=3, sep='/', lead=True):
    "Generate a random PATH"
    if lead:
        path = ['']
    else:
        path = []

    for i in range(minimum, randint(minimum + 1, length + 1)):
        path.append(random_token())

    return sep.join(path)

# -----------------------------------------
# Hashing convenience functions
# -----------------------------------------
def hasher(footprint):
    "hasher used for all objects in project"
    sha1 = hashlib.sha1()
    sha1.update(footprint)
    # return int(sha1.hexdigest(), 16)
    return sha1.hexdigest()

# -----------------------------------------
# Debugging convenience functions
# -----------------------------------------
def until(condition, timeout=5):
    "Wait until condition is true"
    frame = sys._getframe().f_back
    end = time.time() + timeout
    while time.time() < end:
        try:
            result = eval(condition, frame.f_globals, frame.f_locals)
            if result:
                break
        except Exception:
            pass
        time.sleep(0.1)
    else:
        raise RuntimeError(
            'Timeout (%s) while waiting for condition %s' % \
        (timeout, condition))

# -----------------------------------------
# Some convenience functions
# -----------------------------------------
def expath(*path):
    "Join several paths and expand against user and ENV subtitution"
    return os.path.abspath(
        os.path.expanduser(
            os.path.expandvars(
            os.path.join(*path))))
