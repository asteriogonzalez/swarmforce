from watchdog.events import FileSystemEventHandler
from cement.core.controller import CementBaseController, expose

class MonitorController(CementBaseController):
    class Meta:
        label = 'monitor'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = '<Monitirize some running parameters>'
        arguments = [
            ( ['-f', '--file'],
              dict(action='store', help='filename') ),
        ]


    @expose(help='show running internal status')
    def kkaa(self):
        self.app.log.info("Showing internal status ...")



class FileSystemMonitor(FileSystemEventHandler):
    """
    Default event handler used by Cement, that logs all events to the
    application's debug log.  Additional ``*args`` and ``**kwargs`` are passed
    to the parent class.

    :param app: The application object

    """

    def __init__(self, app, *args, **kw):
        FileSystemEventHandler.__init__(self, *args, **kw)
        self.app = app

    def _on_any_event(self, event):
        self.app.log.info("Watchdog Event: %s" % (event.key,))  # pragma: nocover

    def on_modified(self, event):
        self.app.log.info("UPDATE Event: %s" % (event.key,))  # pragma: nocover

    def on_deleted(self, event):
        self.app.log.info("DELETED Event: %s" % (event.key,))  # pragma: nocover

    def on_moved(self, event):
        self.app.log.info("MOVED Event: %s" % (event.key,))  # pragma: nocover
