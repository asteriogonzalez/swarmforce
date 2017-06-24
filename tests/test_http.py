"""Test HTTP message parsing module"""
import types
from io import StringIO
from swarmforce.http import Event, populate, parse, Request, Response


def test_init():
    "Simple Initialization method"
    parser = Event()


def test_parser():
    "Parse some messages and check parsing results"

    parser = Event()

    message = u"""POST /path/script.cgi HTTP/1.0
From: frog@jmarshall.com
User-Agent: HTTPTool/1.0
Content-Type: application/x-www-form-urlencoded
X-Time: 10000000
Content-Length: 32

home=Cosby&favorite+flavor=flies"""

    msg = parse(StringIO(message))
    assert isinstance(msg, Request)

    assert msg == {'body': 'home=Cosby&favorite+flavor=flies',
                      'Content-Length': '32',
                      'From': 'frog@jmarshall.com',
                      'User-Agent': 'HTTPTool/1.0',
                      'path': '/path/script.cgi',
                      'http-version': 'HTTP/1.0',
                      'Content-Type':
                      'application/x-www-form-urlencoded',
                      'X-Time' : '10000000',
                      'method': 'POST'}

    message = u"""GET /search?sourceid=chrome&ie=UTF-8&q=ergterst HTTP/1.1
Host: www.google.com
Connection: keep-alive
Accept: application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5
User-Agent: Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; en-US) AppleWebKit/534.13 (KHTML, like Gecko) Chrome/9.0.597.45 Safari/534.13
Accept-Encoding: gzip,deflate,sdch
Avail-Dictionary: GeNLY2f-
Accept-Language: en-US,en;q=0.8
X-Time: 10000001
"""

    msg = parse(StringIO(message))
    assert isinstance(msg, Request)
    assert msg == {'body': '',
                      'Accept-Language': 'en-US,en;q=0.8',
                      'Accept-Encoding': 'gzip,deflate,sdch',
                      'Connection': 'keep-alive',
                      'Accept': 'application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',  # allowed long line
                      'http-version': 'HTTP/1.1',
                      'Host': 'www.google.com',
                      'Avail-Dictionary': 'GeNLY2f-',
                      'path': '/search?sourceid=chrome&ie=UTF-8&q=ergterst',
                      'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; en-US) AppleWebKit/534.13 (KHTML, like Gecko) Chrome/9.0.597.45 Safari/534.13',  # allowed long line
                      'X-Time' : '10000001',
                      'method': 'GET'}


    message = u"""HTTP/1.1 200 OK
    Date: Mon, 27 Jul 2009 12:28:53 GMT
    Server: Apache/2.2.14 (Win32)
    Last-Modified: Wed, 22 Jul 2009 19:15:56 GMT
    Content-Length: 72
    Content-Type: text/html
    X-Time: 1498328373.00
    Connection: Closed

    <html>
    <body>
    <h1>Hello, World!</h1>
    </body>
    </html>"""

    msg = parse(StringIO(message))
    assert isinstance(msg, Response)
    assert msg == {'body': u'    <html>\n    <body>\n    <h1>Hello, World!</h1>\n    </body>\n    </html>',
                   'Content-Length': '72',
                   'code': '200',
                   'X-Time': '1498328373.00',
                   'http-version': 'HTTP/1.1',
                   'Last-Modified': 'Wed, 22 Jul 2009 19:15:56 GMT',
                   'Connection': 'Closed',
                   'result': 'OK', 'Date': 'Mon, 27 Jul 2009 12:28:53 GMT',
                   'Server': u'Apache/2.2.14 (Win32)',
                   'Content-Type': 'text/html'}


def test_dump():
    "Test message hashing"

    msg1 = Event()
    populate(msg1)
    raw = msg1.dump()

    msg2 = parse(raw)

    assert msg1 == msg1, "Malformed message"


def test_hash():
    "Test message hashing"

    msg1 = Event()
    populate(msg1)

    msg1.hash()

    assert len(msg1['X-Hash']) == 40


def test_key():
    "Test message key"

    msg1 = Event()
    populate(msg1)

    key = msg1.key

    assert isinstance(key, types.TupleType)
    assert len(key) == 4




# End
