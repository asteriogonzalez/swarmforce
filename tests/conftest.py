import pytest
from swarmforce.swarm import World, Worker, \
     MAX_HASH, hash_range, RUNNING, PAUSED

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
def clean_log_file(request, tmpdir):
    "Provide a clean temporary log file that is deleted at the end"

    p = tmpdir.join("test.log")
    filename = os.path.join(p.dirname, p.basename)
    file(filename, 'w').write('')

    def fin():
        os.unlink(filename)

    request.addfinalizer(fin)
    return filename

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

