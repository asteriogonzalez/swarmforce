import os
import time
import pytest
from pprint import pprint
from swarmforce.swarm import World, Worker, \
     MAX_HASH, hash_range, RUNNING, PAUSED


from swarmforce.loggers import getLogger, setup_logging, reset_logs

# print "="*100
# print "CWD1 = ", os.path.abspath(os.getcwd())
# os.chdir(os.environ.get('SF_HOME', '.'))
# print "CWD2 = ", os.path.abspath(os.getcwd())
# print "="*100


log_configfile = setup_logging('test_logging.yaml')
log = getLogger('swarmforce')

@pytest.fixture(scope="function")
def cwd():
    os.chdir(os.environ.get('SF_HOME', '.'))

@pytest.fixture(scope="function")
def clean_logs():
    # print " >> CLEANING LOG FILES"
    reset_logs()

@pytest.fixture(scope="function")
def log_now(request):
    global log
    # print request
    # pprint(request.__dict__)
    # print "-" * 10
    # pprint(request._pyfuncitem.__dict__)

    msg = '>>> BEGIN TEST: %s' % request._pyfuncitem.name
    log.info(msg)

    def fin():
        log.info('<<< END TEST: %s' % request._pyfuncitem.name)

    request.addfinalizer(fin)
    return msg


@pytest.fixture(scope="function")
def world(request):
    "Provide a world that is not shared across all tests"

    world = World()
    world.start()

    def fin():
        world.stop()

    request.addfinalizer(fin)
    return world




@pytest.fixture(scope="function")
def demo_config_file(request, tmpdir):
    "Provide a clean temporary log file that is deleted at the end"

    p = tmpdir.join("test.conf")
    filename = os.path.join(p.dirname, p.basename)
    file(filename, 'w').write('')

    def fin():
        os.unlink(filename)

    request.addfinalizer(fin)
    return filename



# Final setings
#clean_logs()

# End
