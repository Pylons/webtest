# -*- coding: utf-8 -*-
import sys
import six
from six import PY3
from six import text_type
from six.moves import http_cookies

SimpleCookie = http_cookies.SimpleCookie
CookieError = http_cookies.CookieError


def to_bytes(value, charset='latin1'):
    if isinstance(value, text_type):
        return value.encode(charset)
    return value


if PY3:
    from html.entities import name2codepoint
    from urllib.parse import urlencode
    from urllib.parse import splittype
    from urllib.parse import splithost
    import urllib.parse as urlparse
    from http.cookies import _quote as cookie_quote
else:
    from htmlentitydefs import name2codepoint  # noqa
    from urllib import splittype  # noqa
    from urllib import splithost  # noqa
    from urllib import urlencode  # noqa
    from Cookie import _quote as cookie_quote  # noqa
    import urlparse  # noqa


try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping  # noqa


def print_stderr(value):
    if not PY3:
        if isinstance(value, text_type):
            value = value.encode('utf8')
    six.print_(value, file=sys.stderr)

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict  # noqa
