
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

