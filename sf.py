#!/usr/bin/env python

import time
import signal
from cement.core.foundation import CementApp
from cement.core import hook
from cement.utils.misc import init_defaults

from cement.core.controller import CementBaseController, expose
from cement.core.exc import CaughtSignal
from cement.ext.ext_daemon import Environment

# define our default configuration options
defaults = init_defaults('myapp', 'log.logging')
defaults['myapp']['debug'] = False
defaults['myapp']['some_param'] = 'some value'

# capture signals
def my_signal_handler(app, signum, frame):
    # do something with app?
    pass

    # or do someting with signum or frame
    if signum == signal.SIGTERM:
        print("--->> Caught SIGTERM...")
    elif signum == signal.SIGINT:
        print("----->> Caught SIGINT...")


# define any hook functions here
def my_cleanup_hook(app):
    print('running my_cleanup_hook at the end ...')



# some controllers
class MyBaseController(CementBaseController):
    class Meta:
        label = 'base'
        description = "My Application does amazing things!"
        arguments = [
            ( ['-f', '--foo'],
              dict(action='store', help='the notorious foo option') ),
            ( ['-C'],
              dict(action='store_true', help='the big C option') ),
            ]

    @expose(hide=True)
    def default(self):
        self.app.log.info('Inside MyBaseController.default()')
        if self.app.pargs.foo:
            print("Recieved option: foo => %s" % self.app.pargs.foo)

    @expose(help="this command does relatively nothing useful")
    def command1(self):
        self.app.log.info("Inside MyBaseController.command1()")

    @expose(aliases=['cmd2'], help="more of nothing")
    def command2(self):
        self.app.log.info("Inside MyBaseController.command2()")


class MySecondController(CementBaseController):
    class Meta:
        label = 'second'
        stacked_on = 'base'

    @expose(help='this is some command', aliases=['some-cmd'])
    def second_cmd1(self):
        self.app.log.info("Inside MySecondController.second_cmd1")




# define the application class
class MyApp(CementApp):
    class Meta:
        label = 'myapp'
        config_defaults = defaults
        arguments_override_config = True

        extensions = ['mustache', 'daemon', 'memcached', 'json', 'yaml']

        # output_handler = 'mustache'
        template_module = 'myapp.templates'
        template_dirs = [  # default values, but here for clarity
            '~/.myapp/templates',
            '/usr/lib/myapp/templates',
        ]

        hooks = [
            ('pre_close', my_cleanup_hook),
        ]

        base_controller = 'base'
        handlers = [MyBaseController, MySecondController]


def mydaemonize(app, stdout):

    env = Environment(
        user=app.config.get('daemon', 'user'),
        group=app.config.get('daemon', 'group'),
        pid_file=app.config.get('daemon', 'pid_file'),
        dir=app.config.get('daemon', 'dir'),
        umask=app.config.get('daemon', 'umask'),
        stdout=stdout,
    )

    env.switch()

    if '--daemon' in app.argv:
        env.daemonize()

    return env


with MyApp() as app:
    hook.register('signal', my_signal_handler)

    # add arguments to the parser
    # app.args.add_argument('-f', '--foo', action='store', metavar='STR',
                          # help='the notorious foo option')

    # log stuff
    app.log.debug("About to run my myapp application!")

    # run the application
    #app.daemonize()
    stdout = '/tmp/myapp.out'
    env = mydaemonize(app, stdout)
    app.run()

    # continue with additional application logic
    if app.pargs.foo:
        app.log.info("Hi!!, we have received option: foo => %s" % app.pargs.foo)

    # expected you write a ~/.myapp.conf
    print(app.config.get('myapp', 'foo'))  # will be overriden by command line
    print(app.config.get('myapp', 'bazz'))
    print(app.config.get('hello', 'a'))

    app.log.info('This is my info message', __name__)


    # ~/.myapp/templates/default.m

    data = app.pargs.__dict__
    app.render(data, 'default.m')


    try:
        for i in range(60):
            print(i)
            time.sleep(1)
    except CaughtSignal as e:
        # do soemthing with e.signum, e.frame
        print "Signal: %s" % e.signum


    # print('Sending an email!')
    # # send an email message
    # app.mail.send('This is my message',
        # subject='This is my subject',
        # to=['asterio.gonzalez@gmail.com'],
        # from_addr='asterio.gonzalez@gmail.com',
        # #cc=['him@example.com', 'her@example.com'],
        # #bcc=['boss@example.com']
        # )

    print('-End-')
