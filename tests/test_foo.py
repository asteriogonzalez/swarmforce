"""This a demo module for testing pytest configuration"""
import os
import sys
import subprocess
# from swarmforce.foo import Foo

# foo = 1


# def test_foo():
    # "A simple function"
    # parser = Foo()
    # parser.bar()


def test_subprocess_inherance():

    os.environ['FOO'] = 'foo'
    filename = os.path.abspath(__file__)
    p = subprocess.Popen(['python', filename])
    p.wait()
    print "Parent End"
    fo = 1


def main():
    print "Child $FOO = %s" % (os.environ.get('FOO'))
    assert os.environ.get('FOO') == 'foo'

if __name__ == '__main__':
    main()


# End
