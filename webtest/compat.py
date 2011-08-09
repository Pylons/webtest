# -*- coding: utf-8 -*-
import sys

if sys.version_info[0] > 2:
    PY3 = True
    class Base(object):
        def __init__(self, content_type='text/html', *args, **kwargs):
            self.content_type = content_type
            self.charset = self.body = self.url = None
            self.request = None
    class Request(Base):
        def __init__(self, *args, **kwargs):
            Base.__init__(self, *args, **kwargs)
            self.request = Base()
    Response = Request
    DictType = dict
    StringType = bytes
    TupleType = tuple
    ListType = list
    from io import StringIO
    import urllib.parse as urlparse
    from http.cookies import SimpleCookie, CookieError
    from http.cookies import _quote as cookie_quote
else:
    PY3 = False
    from types import DictType, StringType, TupleType, ListType
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
