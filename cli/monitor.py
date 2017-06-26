
from cement.core.controller import CementBaseController, expose

class MonitorController(CementBaseController):
    class Meta:
        label = 'second'
        stacked_on = 'base'

    @expose(help='show running internal status')
    def show(self):
        self.app.log.info("Showing internal status ...")

