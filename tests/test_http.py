"""Test HTTP message parsing module"""
from io import StringIO
from swarmforce.http import HTTPMessage, populate

def test_init():
    "Simple Initialization method"
    parser = HTTPMessage()


def test_parser():
    "Parse some messages and check parsing results"

    parser = HTTPMessage()

    message = u"""POST /path/script.cgi HTTP/1.0
From: frog@jmarshall.com
User-Agent: HTTPTool/1.0
Content-Type: application/x-www-form-urlencoded
Content-Length: 32

home=Cosby&favorite+flavor=flies"""

    parser.parse(StringIO(message))
    assert parser == {'body': 'home=Cosby&favorite+flavor=flies',
                      'Content-Length': '32',
                      'From': 'frog@jmarshall.com',
                      'User-Agent': 'HTTPTool/1.0',
                      'path': '/path/script.cgi',
                      'http-version': 'HTTP/1.0',
                      'Content-Type':
                      'application/x-www-form-urlencoded',
                      'method': 'POST'}

    message = u"""GET /search?sourceid=chrome&ie=UTF-8&q=ergterst HTTP/1.1
Host: www.google.com
Connection: keep-alive
Accept: application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5
User-Agent: Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; en-US) AppleWebKit/534.13 (KHTML, like Gecko) Chrome/9.0.597.45 Safari/534.13
Accept-Encoding: gzip,deflate,sdch
Avail-Dictionary: GeNLY2f-
Accept-Language: en-US,en;q=0.8
"""

    parser = HTTPMessage()
    parser.parse(StringIO(message))
    assert parser == {'body': '',
                      'Accept-Language': 'en-US,en;q=0.8',
                      'Accept-Encoding': 'gzip,deflate,sdch',
                      'Connection': 'keep-alive',
                      'Accept': 'application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',  # allowed long line
                      'http-version': 'HTTP/1.1',
                      'Host': 'www.google.com',
                      'Avail-Dictionary': 'GeNLY2f-',
                      'path': '/search?sourceid=chrome&ie=UTF-8&q=ergterst',
                      'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; en-US) AppleWebKit/534.13 (KHTML, like Gecko) Chrome/9.0.597.45 Safari/534.13',  # allowed long line
                      'method': 'GET'}


def test_dump():
    "Test message hashing"

    msg1 = HTTPMessage()
    populate(msg1)
    raw = msg1.dump()

    msg2 = HTTPMessage()
    msg2.parse(raw)

    assert msg1 == msg1


def test_hash():
    "Test message hashing"

    msg1 = HTTPMessage()
    populate(msg1)

    msg1.hash()

    assert len(msg1['X-Hash']) == 40


# End
