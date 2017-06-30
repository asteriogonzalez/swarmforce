
from swarmforce.swarm import World, Worker, \
     MAX_HASH, hash_range, RUNNING, PAUSED

from swarmforce.loggers import getLogger
log = getLogger('swarmforce')


class Boss(Worker):
    "A client agent"

    def __init__(self):
        Worker.__init__(self)
        self.add_response_handler('2\d\d$', self.response_OK)
        self.hits = 0

    def response_OK(self, response):
        request = response.request
        log.info('%s ---> %s', request.body, response.body)
        self.response = response.body
        self.hits += 1
        log.info('hits: %s', self.hits)


class EvalWorker(Worker):
    "A server agent"

    def dispatch_request(self, event):
        result = eval(event.body)
        answer = event.answer()
        answer.body = unicode(result)
        log.info(answer.dump())

# End
