# -*- coding: utf-8 -*-
from webtest.compat import MutableMapping, name2codepoint, urlencode
from json import dumps
from six import binary_type
from six import text_type
from six import PY3
import functools
import re


class CleverCookieDict(MutableMapping):
    def __init__(self, morsels):
        self.morsels = morsels

    def __getitem__(self, k):
        return self.morsels[k].value

    def __setitem__(self, k, v):
        morsel = self.morsels.setdefault(k, Morsel())
        morsel.set(k, v)

    def __delitem__(self, k):
        del self.morsels[k]

    def __iter__(self):
        return iter(self.morsels)

    def __len__(self):
        return len(self.morsels)

    def __repr__(self):
        return "{0.__class__.__name__}({1!r})".format(
            self, dict((k, v.value) for k, v in self.morsels.items()))


class NoDefault(object):
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
    if isinstance(value, text_type):
        return value
    elif isinstance(value, binary_type):
        return value.decode('utf8')
    else:
        return str(value)


entity_pattern = re.compile(r"&(\w+|#\d+|#[xX][a-fA-F0-9]+);")


def html_unquote(v):
    """
    Unquote entities in HTML.
    """
    to_chr = chr if PY3 else unichr

    def repl(match):
        s = match.group(1)
        if s.startswith("#"):
            if s[1].lower() == "x":
                s = int(s[2:], 16)
            else:
                s = int(s[1:])
        elif s in name2codepoint:
            s = name2codepoint[s]
        else:
            return
        return to_chr(s)
    return entity_pattern.sub(repl, v)


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
                    if isinstance(v, text_type):
                        v = v.encode(charset)
                    encoded_params.append((k, v))
                params = encoded_params
        params = urlencode(params, doseq=True)
    return params

_attr_re = re.compile(
        (r'([^= \n\r\t]+)[ \n\r\t]*(?:=[ \n\r\t]*(?:"([^"]*)"|\'([^\']*)'
         r'\'|([^"\'][^ \n\r\t>]*)))?'), re.S)


def parse_attrs(text):
    attrs = {}
    for match in _attr_re.finditer(text):
        attr_name = match.group(1).lower()
        attr_body = match.group(2) or match.group(3)
        attr_body = html_unquote(attr_body or '')
        # python <= 2.5 doesn't like **dict when the keys are unicode
        # so cast str on them. Unicode field attributes are not
        # supported now (actually they have never been supported).
        attrs[str(attr_name)] = attr_body
    return attrs


def make_pattern(pat):
    if pat is None:
        return None
    if isinstance(pat, binary_type):
        pat = pat.decode('utf8')
    if isinstance(pat, text_type):
        pat = re.compile(pat)
    if hasattr(pat, 'search'):
        return pat.search
    if hasattr(pat, '__call__'):
        return pat
    assert 0, (
        "Cannot make callable pattern object out of %r" % pat)
