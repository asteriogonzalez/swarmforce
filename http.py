""" HTTP message parser"""
import re
import types
import hashlib
from io import StringIO
from random import choice
from swarmforce.misc import random_path, random_token

class HTTPMessage(dict):
    """Parse HTTP messages and store info in a dict
    like object."""
    _rexp = re.compile(r"(?P<name>.*?): (?P<value>.*)", re.DOTALL | re.I | re.M)

    def __init__(self, *args, **kw):
        self['body'] = u''
        dict.__init__(self, *args, **kw)

    def parse(self, stream):
        """Parse HTTP message from stream."""
        if isinstance(stream, types.StringTypes):
            stream = StringIO(unicode(stream))

        cmd = stream.readline().strip()
        self['method'], self['path'], self['http-version'] = cmd.split()
        line = stream.readline().strip()
        while line:
            match = self._rexp.match(line)
            if match:
                data = match.groups()
                self[data[0]] = data[1]
            else:
                raise RuntimeError('Error parsing HTTP header: %s' % line)

            line = stream.readline().strip()

        self['body'] = body = stream.read()
        length = int(self.get('Content-Length', 0))

        assert not length or len(body) == length

    def dump(self, exclude_headers=None):
        """Dump HTTP message into a Stream"""
        lines = []
        lines.append("%(method)s %(path)s %(http-version)s" % self)

        excluded = ['method', 'path', 'http-version', 'body']

        excluded = set(excluded)
        if exclude_headers:
            excluded.difference_update(exclude_headers)

        for key in excluded.symmetric_difference(self.keys()):
            value = self[key]
            line = '%s: %s' % (key, value)
            lines.append(line)

        body = self.body
        if body:
            lines.append('')
            lines.append(body)

        return '\n'.join(lines)

    def hash(self, exclude_headers=None):
        """Get the hash of the message, skiping some headers"""
        if exclude_headers:
            exclude_headers.append('X-Hash')
        else:
            exclude_headers = ['X-Hash']

        raw = self.dump(exclude_headers)
        sha1 = hashlib.sha1()
        sha1.update(raw)
        hash_ = sha1.hexdigest()
        self['X-Hash'] = hash_
        return hash_



    def __getattr__(self, key):
        # if hasattr(self, key):
            # return getattr(self, key)
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value



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
