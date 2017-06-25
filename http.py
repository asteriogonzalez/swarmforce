""" HTTP message parser"""
import re
import types
import time
from io import StringIO
from random import choice
from swarmforce.misc import random_path, random_token, hasher
from swarmforce.loggers import getLogger

log = getLogger('swarmforce')

CODE_OK = '200'

class Event(dict):
    """Parse HTTP messages and store info in a dict
    like object."""

    statusline_fmt = "%(method)s %(path)s %(http-version)s"

    def __init__(self, *args, **kw):
        kw.setdefault('http-version', 'HTTP/1.1')
        kw.setdefault('body', u'')

        if 'X-Time' not in kw:
            kw['X-Time'] = str(time.time())
        dict.__init__(self, *args, **kw)


    def dump(self, exclude_headers=None, lines=None):
        """Dump HTTP message into a Stream"""
        if lines is None:
            lines = []

        lines.append(self.statusline_fmt % self)

        excluded = set(['method', 'path', 'http-version', 'body', 'code', 'result'])
        if exclude_headers:
            excluded.update(exclude_headers)

        body = self.body
        if body:
            self['Content-Length'] = len(body)

        keys = list(excluded.symmetric_difference(self.keys()))
        keys.sort()

        for key in keys:
            if key in self:
                value = self[key]
                line = '%s: %s' % (key, value)
                lines.append(line)

        body = self.body
        if body:
            lines.append('')
            lines.append(body)

        return '\n'.join(lines)

    def hash(self, exclude_headers=None, inplace=True):
        """Get the hash of the message, skiping some headers"""
        if exclude_headers:
            exclude_headers.append('X-Hash')
        else:
            exclude_headers = ['X-Hash']

        footprint = self.dump(exclude_headers)
        hash_ = hasher(footprint)
        if inplace:
            self['X-Hash'] = hash_
        return hash_

    def sane(self):
        "Check event sanity"
        hash_1 = self.get('X-Hash')
        if hash_1 is not None:
            hash_2 = self.hash(inplace=False)
            if hash_1 != hash_2:
                log.error('HASH %s MISTMATCH: %s', hash_2, self.dump())
                return False
            else:
                log.debug('HASH OK: %s', hash_1)
        return True

    @property
    def statusline(self):
        """returns the statusline of the message that
        is used to determine the class of message (e.g Request, Response)
        according to HTTP protocol"""
        return '%(method)s %(path)s' % self

    def __getattr__(self, key):
        # if hasattr(self, key):
            # return getattr(self, key)
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value



class Request(Event):
    """A request HTTP style class."""
    copy_keys = ['http-version', 'X-Client']
    statusline_fmt = "%(method)s %(path)s %(http-version)s"
    response = None  # belong to class. Override by instance.answer()

    def answer(self, code=CODE_OK, result='OK'):
        """Create an Response message to this Request"""
        log.info('Creating response for %s', self.dump())
        msg = Response(code=code, result=result)
        for key in self.copy_keys:
            if self.has_key(key):
                msg[key] = self[key]

        msg['X-Request-Id'] = self['X-Hash']

        self.__dict__['response'] = msg
        return msg


    @property
    def key(self):
        "Return a hashable object that identify this message"
        # return (self.method, self['X-Time'], self.path, self.get('X-NewPath'))
        return self.hash()


class Response(Event):
    """A response HTTP style class."""

    statusline_fmt = "%(http-version)s %(code)s %(result)s"

    @property
    def key(self):
        "Return a hashable object that identify this message"
        return (self['code'], self['X-Time'], )

RE_HEADER = re.compile(r"(?P<name>.*?): (?P<value>.*)",
                       re.DOTALL | re.I)

RE_REQ = re.compile(r"(?P<method>\S+)\s+(?P<path>\S+)\s+(?P<http_version>HTTP\/.+)$",
                    re.DOTALL | re.I)
RE_RES = re.compile(r"(?P<http_version>HTTP\/\S+)\s+(?P<code>\S+)\s+(?P<result>.*)$",
                    re.DOTALL | re.I)

PARSE_MAP = dict()
PARSE_MAP[RE_REQ] = Request
PARSE_MAP[RE_RES] = Response

def parse(stream):
    """Parse HTTP message from stream."""
    if isinstance(stream, types.StringTypes):
        stream = StringIO(unicode(stream))

    statusline = stream.readline().strip()
    for _re, klass in PARSE_MAP.items():
        match = _re.match(statusline)
        if match:
            match = match.groupdict()
            match['http-version'] = match.pop('http_version')
            msg = klass(**match)
            break
    else:
        raise RuntimeError('Unknown message type: %s' % statusline)

    line = stream.readline().strip()
    while line:
        match = RE_HEADER.match(line)
        if match:
            data = match.groups()
            msg[data[0]] = data[1]
        else:
            raise RuntimeError('Error parsing HTTP header: %s' % line)

        line = stream.readline().strip()

    msg['body'] = body = stream.read()
    length = int(msg.get('Content-Length', 0))

    assert not length or len(body) == length

    return msg



def populate(msg):
    """Populate the message using random data"""
    msg.method = choice(['GET', 'POST'])
    msg['http-version'] = choice(['HTTP/1.0', 'HTTP/1.1'])
    msg.path = random_path().lower()
    msg.Host = random_path(length=5, sep='.', lead=False).lower()

    msg['Accept-Language'] = choice(['en-US,en;q=0.8', 'es-ES,es;q=0.7'])

    msg['User-Agent'] = choice(['HTTPTool/1.0', 'Mozilla/5.0'])
    msg.body = body = random_token(200)
    msg['Content-Length'] = len(body)


# End
