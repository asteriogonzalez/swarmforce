import os
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
