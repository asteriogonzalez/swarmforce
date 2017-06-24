"""This a demo module for testing pytest configuration"""
from swarmforce.foo import Foo

foo = 1


def test_foo():
    "A simple function"
    parser = Foo()
    parser.bar()


# End
