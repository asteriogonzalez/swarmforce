#!/usr/bin/env python

import sys
import time
import os
import signal
import uuid  # get_node() id
import hashlib
import random

from pprint import pprint
from cement.core.foundation import CementApp
from cement.core import hook
from cement.utils.misc import init_defaults

from cement.core.controller import CementBaseController, expose
from cement.core.exc import CaughtSignal, FrameworkError
from cement.ext.ext_daemon import Environment
from cement.ext.ext_watchdog import WatchdogEventHandler

# add root of code imports
sys.path.insert(0, os.path.sep.join(os.path.abspath(__file__).split(os.path.sep)[:-3]))

# project defined Handlers
from monitor import MonitorController, FileSystemMonitor
from show import ShowController
from swarmforce.misc import expath
from swarmforce.swarm import Layout, active, dead
from swarmforce.loggers import getLogger, log_configfile

os.chdir(os.environ.get('SF_HOME', '.'))

log = getLogger('swarmforce')
# print "="* 50
# print "log_configfile", log_configfile
# print "="* 50


# define our default configuration options
defaults = init_defaults('swarmforce', 'log.logging')
defaults['swarmforce']['debug'] = False
defaults['swarmforce']['workers'] = '1'
defaults['swarmforce']['root'] = '.'


# -----------------------------------------
# Hooks and Signals
# -----------------------------------------
def my_signal_handler(app, signum, frame):

    # or do someting with signum or frame
    if signum == signal.SIGTERM:
        print("--->> Caught SIGTERM...")
    elif signum == signal.SIGINT:
        print("----->> Caught SIGINT...")


def my_setup_hook(app):
    """Prepare any missing piece from config before run the application."""

    # set some useful parameters
    sha = hashlib.sha1()
    sha.update('%x' % uuid.getnode())
    app.nodeid = sha.hexdigest()

    sha.update('%x' % os.getpid())
    app.workerid = sha.hexdigest()

    # Home FS layout
    app.root = os.path.abspath(
        os.path.expanduser(app.config.get('swarmforce', 'root')))
    app.layout = layout = Layout(app.root, app.nodeid, app.workerid)

    # used config files
    used_config_files = layout.used_config_files = list()
    layout.last_used_config_files = None
    for path in app._meta.config_files:
        if os.path.exists(path):
            used_config_files.append(path)
            layout.last_used_config_files = path

    layout.setup()
    layout.update_pid_file()

    # replace logger
    # app.log = log
    #app.log.error('TEST')

    # create the folder of pid_file
    # pid_file = app.config.get('daemon', 'pid_file')
    # dirname = os.path.dirname(pid_file)
    # if not os.path.exists(dirname):
        # os.makedirs(dirname)

    # # check if there's a dead pid and delete it to start clean
    # if os.path.exists(pid_file):
        # pid = int(file(pid_file, 'r').read())
        # if psutil.pid_exists(pid):
            # raise RuntimeError('Process %s already running in %s' % (pid, pid_file))
        # os.unlink(pid_file)


def my_cleanup_hook(app):
    """Clean any resources necessary at the end of the application."""


# -----------------------------------------
# The Default base handler
# -----------------------------------------
class DefaultController(CementBaseController):
    class Meta:
        label = 'base'
        description = "Swarm Force Application command line client"
        arguments = [
            ( ['-f', '--file'],
              dict(action='store', help='filename') ),

            ( ['-w', '--workers'],
              dict(action='store', help='num workers', default='1'),  ),

            ( ['--force'],
              dict(action='store', help='force operation') ),

            ( ['--timeout'],
              dict(action='store', help='timeout in seconds') ),


            ]

    @expose(hide=True)  # not shown with --help
    def default(self):
        "Default handler when no other commands are specified."
        self.app.log.info('Inside DefaultController.default()')

        if self.app.pargs.file:
            print("Recieved option: file => %s" % self.app.pargs.file)


    @expose(help="Start one or mode workers in this node")
    def start(self):
        """Start one or mode workers in this node."""
        if self.app.pargs.workers:
            workers = int(self.app.pargs.workers)
        else:
            workers = 1

        if workers == 1:
            self.app.log.info('Start node %s with %s worker' % (self.app.nodeid, workers))
        else:
            self.app.log.info('Start node %s with %s workers' % (self.app.nodeid, workers))

    @expose(help="Stop all workers")
    def stop(self):
        """Stop all workers from the node."""
        app.log.info('Stop node')

    @expose(help="Stop all workers")
    def restart(self):
        """Start one or mode workers in this nodee."""
        self.stop()
        self.start()






# -----------------------------------------
# The Application Class
# -----------------------------------------
class SwarmForce(CementApp):
    class Meta:
        label = 'swarmforce'
        config_defaults = defaults
        config_extension = '.conf'

        # NOTE: remenber that cement will PROCESS and MERGE ALL config files
        config_files = [
            # default cement settings
            expath('/', 'etc', label, '%s%s' % (label, config_extension)),
            expath('~', '.%s' % label, 'config'),
            expath('~', '.%s%s' % (label, config_extension)),

            # add local directory config
            expath('%s%s' % (label, config_extension)),
        ]

        arguments_override_config = True

        extensions = ['mustache', 'daemon', 'memcached',
                      'json', 'yaml',
                      # 'watchdog',
                      ]

        # output_handler = 'mustache'
        # template_module = 'swarmforce.templates'
        # template_dirs = [  # default values, but here for clarity
            # '~/.swarmforce/templates',
            # '/usr/lib/swarmforce/templates',
        # ]

        hooks = [
            ('pre_run', my_setup_hook),
            ('pre_close', my_cleanup_hook),
        ]

        watchdog_paths = [
            ('.', FileSystemMonitor),
        ]

        base_controller = 'base'
        handlers = [DefaultController, MonitorController, ShowController]


# -----------------------------------------
# Starting the Application
# -----------------------------------------
app = None
def main():
    "Main entry point of application"
    global app

    # print('LOGGING_CFG[pid [%s] = %s'% (os.getpid(), os.environ.get('LOGGING_CFG')) )
    log.info('>>> LOGGING_CFG[pid [%s] = %s', os.getpid(), os.environ.get('LOGGING_CFG') )


    with SwarmForce() as app:
        try:
            hook.register('signal', my_signal_handler)
            app.run()

            app.daemonize()

            try:
                killtimeout = app.config.get('swarmforce', 'killtimeout')
                killtimeout = killtimeout and float(killtimeout)
                now = time.time()
                for i in xrange(100):
                    log.info('pid[%s] loop: %s' % (os.getpid(), i))

                    # print 'print: pid[%s] loop: %s' % (os.getpid(), i)
                    time.sleep(1)
                    if random.random() < 0.5:
                        app.layout.clean_dead()

                    if killtimeout and \
                       time.time() > now + killtimeout:
                        print "-Timeout-"
                        break


            except CaughtSignal as e:
                print(e)

        except CaughtSignal as e:
            # determine what the signal
            # and do something with it
            from signal import SIGINT, SIGABRT

            if e.signum == SIGINT:
                # do something... maybe change the exit code?
                app.exit_code = 110
            elif e.signum == SIGABRT:
                # do something else...
                app.exit_code = 111

        except FrameworkError as e:
            # do something when a framework error happens
            print("FrameworkError => %s" % e)

            # and maybe set the exit code to something unique as well
            app.exit_code = 300

        finally:
            # Maybe we want to see a full-stack trace for the above
            # exceptions, but only if --debug was passed?
            if app.debug:
                import traceback
                traceback.print_exc()


if __name__ == '__main__':
    main()

