
from StringIO import StringIO

from cement.core.controller import CementBaseController, expose

class ShowController(CementBaseController):
    class Meta:
        label = 'show'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = '<Show diferent node and worker information>'
        arguments = [
            ( ['-f', '--file'],
              dict(action='store', help='filename') ),
        ]

    @expose(help='show current config')
    def config(self):
        """Show or save configuration file."""
        self.app.log.info("Showing current configuration information ...")
        if self.app.pargs.file:
            with open(app.pargs.file, 'w') as configfile:
                self.app.config.write(configfile)
        else:
            out = StringIO()
            self.app.config.write(out)
            out.read()
            print(out.buf)

    @expose(help='show current roadmap')
    def roadmap(self):
        """Show the current roadmap."""
        self.app.log.info("Showing current ROADMAP...")


