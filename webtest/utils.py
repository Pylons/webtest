# -*- coding: utf-8 -*-
from json import dumps
import functools
import re
import six
from six.moves import html_parser

from webtest.compat import urlencode


unescape_html = html_parser.HTMLParser().unescape


class NoDefault(object):
    """Sential to uniquely represent no default value."""

    def __repr__(self):
        return '<NoDefault>'

NoDefault = NoDefault()


def json_method(method):
    """Do a %(method)s request.  Very like the
    :class:`~webtest.TestApp.%(lmethod)s` method.

    ``params`` are dumps to json and put in the body of the request.
    Content-Type is set to ``application/json``.

    Returns a ``webob.Response`` object.
    """

    @functools.wraps(json_method)
    def wrapper(self, url, params=NoDefault, **kw):
        content_type = 'application/json'
        if params is not NoDefault:
            params = dumps(params)
        kw.update(
            params=params,
            content_type=content_type,
            upload_files=None,
        )
        return self._gen_request(method, url, **kw)

    subst = dict(lmethod=method.lower(), method=method)
    wrapper.__doc__ = json_method.__doc__ % subst
    wrapper.__name__ = str('%(lmethod)s_json')

    return wrapper


def stringify(value):
    if isinstance(value, six.text_type):
        return value
    elif isinstance(value, six.binary_type):
        return value.decode('utf8')
    else:
        return str(value)


entity_pattern = re.compile(r"&(\w+|#\d+|#[xX][a-fA-F0-9]+);")


def encode_params(params, content_type):
    if params is NoDefault:
        return ''
    if isinstance(params, dict) or hasattr(params, 'items'):
        params = list(params.items())
    if isinstance(params, (list, tuple)):
        if content_type:
            content_type = content_type.lower()
            if 'charset=' in content_type:
                charset = content_type.split('charset=')[1]
                charset = charset.strip('; ').lower()
                encoded_params = []
                for k, v in params:
                    if isinstance(v, six.text_type):
                        v = v.encode(charset)
                    encoded_params.append((k, v))
                params = encoded_params
        params = urlencode(params, doseq=True)
    return params


_attr_re = re.compile(
        r'([^= \n\r\t]+)[ \n\r\t]*(?:=[ \n\r\t]*(?:"([^"]*)"|\'([^\']*)'
        r'\'|([^"\'][^ \n\r\t>]*)))?', re.S)


def parse_attrs(text):
    attrs = {}
    for match in _attr_re.finditer(text):
        attr_name = match.group(1).lower()
        attr_body = match.group(2) or match.group(3)
        attr_body = unescape_html(attr_body or '')
        attrs[attr_name] = attr_body
    return attrs


def make_pattern(pat):
    """Find element pattern can be a regex or a callable."""
    if pat is None:
        return None
    if isinstance(pat, six.binary_type):
        pat = pat.decode('utf8')
    if isinstance(pat, six.text_type):
        pat = re.compile(pat)
    if hasattr(pat, 'search'):
        return pat.search
    if hasattr(pat, '__call__'):
        return pat
    raise ValueError(
        "Cannot make callable pattern object out of %r" % pat)
