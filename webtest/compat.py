# -*- coding: utf-8 -*-
import sys
import six
from six import PY3
from six import text_type
from six import binary_type
from six.moves import http_client
from six.moves import BaseHTTPServer
from six.moves import SimpleHTTPServer

try:
    from json import loads
    from json import dumps
except ImportError:
    try:
        from simplejson import loads
        from simplejson import dumps
    except ImportError:
        loads = None
        dumps = None


def to_bytes(value, charset='latin1'):
    if isinstance(value, text_type):
        return value.encode(charset)
    return value

to_string = six.u


def join_bytes(sep, l):
    l = [to_bytes(e) for e in l]
    return to_bytes(sep).join(l)

if PY3:
    string_types = (str,)
    from html.entities import name2codepoint
    from io import StringIO
    from io import BytesIO
    from urllib.parse import urlencode
    from urllib.parse import splittype
    from urllib.parse import splithost
    import urllib.parse as urlparse
    from http.cookies import SimpleCookie, CookieError
    from http.cookies import _quote as cookie_quote


else:
    string_types = basestring
    from htmlentitydefs import name2codepoint
    from urllib import splittype
    from urllib import splithost
    from urllib import urlencode
    from Cookie import SimpleCookie, CookieError
    from Cookie import _quote as cookie_quote
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO
    BytesIO = StringIO
    import urlparse


def print_stderr(value):
    if not PY3:
        if isinstance(value, text_type):
            try:
                value = value.encode('utf8')
            except:
                value = repr(value)
    six.print_(value, file=sys.stderr)

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict

try:
    from unittest import TestCase
    from unittest import skipIf
except ImportError:
    try:
        from unittest2 import TestCase
        from unittest2 import skipIf
    except ImportError:
        from unittest import TestCase
        def skipIf(condition, message):
            if condition:
                return None
            def wrapper(func):
                return func
            return wrapper
