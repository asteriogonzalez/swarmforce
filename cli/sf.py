#!/usr/bin/env python

import time
import os
import signal
import psutil
from StringIO import StringIO
from cement.core.foundation import CementApp
from cement.core import hook
from cement.utils.misc import init_defaults

from cement.core.controller import CementBaseController, expose
from cement.core.exc import CaughtSignal, FrameworkError
from cement.ext.ext_daemon import Environment

# project defined Handlers
from monitor import MonitorController

# define our default configuration options
defaults = init_defaults('swarmforce', 'log.logging')
defaults['swarmforce']['debug'] = False
defaults['swarmforce']['some_param'] = 'some value'

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

    # create the folder of pid_file
    pid_file = app.config.get('daemon', 'pid_file')
    dirname = os.path.dirname(pid_file)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    # check if there's a dead pid and delete it to start clean
    if os.path.exists(pid_file):
        pid = int(file(pid_file, 'r').read())
        if psutil.pid_exists(pid):
            raise RuntimeError('Process %s already running in %s' % (pid, pid_file))
        os.unlink(pid_file)


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

            ]

    @expose(hide=True)  # not shown with --help
    def default(self):
        "Default handler when no other commands are specified."
        self.app.log.info('Inside DefaultController.default()')

        if self.app.pargs.file:
            print("Recieved option: file => %s" % self.app.pargs.file)


    @expose(aliases=['showcfg'], help="Show the whole configuration")
    def show_config(self):
        """Show or save configuration file."""
        if app.pargs.file:
            with open(app.pargs.file, 'w') as configfile:
                app.config.write(configfile)
        else:
            out = StringIO()
            app.config.write(out)
            out.read()
            print(out.buf)





# -----------------------------------------
# The Application Class
# -----------------------------------------
class SwarmForce(CementApp):
    class Meta:
        label = 'swarmforce'
        config_defaults = defaults
        arguments_override_config = True

        extensions = ['mustache', 'daemon', 'memcached', 'json', 'yaml']

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

        base_controller = 'base'
        handlers = [DefaultController, MonitorController]



# -----------------------------------------
# Starting the Application
# -----------------------------------------


app = None
def main():
    "Main entry point of application"
    global app

    with SwarmForce() as app:
        try:
            hook.register('signal', my_signal_handler)
            app.run()
            app.daemonize()

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

