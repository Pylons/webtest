# -*- coding: utf-8 -*-
import sys

if sys.version_info[0] > 2:
    PY3 = True
    string_types = (str,)
    text_type = str
    binary_type = bytes
    DictType = dict
    StringType = bytes
    TupleType = tuple
    ListType = list
    from io import StringIO
    from urllib.parse import urlencode
    import urllib.parse as urlparse
    from http.client import HTTPConnection
    from http.client import CannotSendRequest
    from http.server import HTTPServer
    from http.server import SimpleHTTPRequestHandler
    from http.cookies import SimpleCookie, CookieError
    from http.cookies import _quote as cookie_quote
else:
    PY3 = False
    string_types = basestring
    text_type = unicode
    binary_type = str
    from types import DictType, StringType, TupleType, ListType
    from urllib import urlencode
    from httplib import HTTPConnection
    from httplib import CannotSendRequest
    from BaseHTTPServer import HTTPServer
    from SimpleHTTPServer import SimpleHTTPRequestHandler
    from Cookie import SimpleCookie, CookieError
    from Cookie import _quote as cookie_quote
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO
    import urlparse



def print_stderr(value):
    if PY3:
        exec('print(value, file=sys.stderr)')
    else:
        exec('print >> sys.stderr, value')
