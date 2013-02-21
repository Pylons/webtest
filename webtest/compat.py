# -*- coding: utf-8 -*-
import sys
import six
from six import PY3
from six import text_type
from six import binary_type
from six import string_types
from six.moves import http_client
from six.moves import http_cookies
from six.moves import BaseHTTPServer
from six.moves import SimpleHTTPServer
from six.moves import cStringIO
from json import loads
from json import dumps

StringIO = BytesIO = cStringIO  # Also define BytesIO for py2.x
SimpleCookie = http_cookies.SimpleCookie
CookieError = http_cookies.CookieError


def to_bytes(value, charset='latin1'):
    if isinstance(value, text_type):
        return value.encode(charset)
    return value


if PY3:
    from html.entities import name2codepoint
    from io import BytesIO
    from urllib.parse import urlencode
    from urllib.parse import splittype
    from urllib.parse import splithost
    import urllib.parse as urlparse
else:
    from htmlentitydefs import name2codepoint
    from urllib import splittype
    from urllib import splithost
    from urllib import urlencode
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
