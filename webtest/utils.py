import functools
import re
from json import dumps
import urllib.parse

import webob

from webtest.compat import urlencode


class NoDefault:
    """Sentinel to uniquely represent no default value."""

    def __repr__(self):
        return '<NoDefault>'

NoDefault = NoDefault()


def json_method(method):
    """Do a %(method)s request.  Very like the
    :class:`~webtest.TestApp.%(lmethod)s` method.

    ``params`` are dumped to json and put in the body of the request.
    Content-Type is set to ``application/json``.

    Returns a :class:`webtest.TestResponse` object.
    """

    def wrapper(self, url, params=NoDefault, **kw):
        kw.setdefault('content_type', 'application/json')
        if params is not NoDefault:
            params = dumps(params, cls=self.JSONEncoder)
        kw.update(
            params=params,
            upload_files=None,
        )
        return self._gen_request(method, url, **kw)

    subst = dict(lmethod=method.lower(), method=method)

    try:
        wrapper.__doc__ = json_method.__doc__ % subst
    except TypeError:
        pass

    wrapper.__name__ = str('%(lmethod)s_json' % subst)

    return wrapper


def stringify(value):
    if isinstance(value, str):
        return value
    elif isinstance(value, bytes):
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
                    if isinstance(v, str):
                        v = v.encode(charset)
                    encoded_params.append((k, v))
                params = encoded_params
        params = urlencode(params, doseq=True)
    return params


def build_params(url, params):
    if not isinstance(params, str):
        params = urlencode(params, doseq=True)
    if '?' in url:
        url += '&'
    else:
        url += '?'
    url += params
    return url


def make_pattern(pat):
    """Find element pattern can be a regex or a callable."""
    if pat is None:
        return None
    if isinstance(pat, bytes):
        pat = pat.decode('utf8')
    if isinstance(pat, str):
        pat = re.compile(pat)
    if hasattr(pat, 'search'):
        return pat.search
    if hasattr(pat, '__call__'):
        return pat
    raise ValueError(
        "Cannot make callable pattern object out of %r" % pat)


class _RequestCookieAdapter:
    """
    cookielib.CookieJar support for webob.Request
    """
    def __init__(self, request):
        self._request = request
        self.origin_req_host = request.host

    def is_unverifiable(self):
        return True  # sure? Why not?

    @property
    def unverifiable(self):  # NOQA
        # This is undocumented method that Python 3 cookielib uses
        return True

    def get_full_url(self):
        return self._request.url

    @property
    def host(self):
        return self.origin_req_host

    def get_host(self):
        return self.origin_req_host
    get_origin_req_host = get_host

    def add_unredirected_header(self, key, header):
        self._request.headers[key] = header

    def has_header(self, key):
        return key in self._request.headers

    def get_type(self):
        return self._request.scheme

    @property
    def type(self):  # NOQA
        # This is undocumented method that Python 3 cookielib uses
        return self.get_type()

    def header_items(self):  # pragma: no cover
        # This is unused on most python versions
        return self._request.headers.items()


class _ResponseCookieAdapter:
    """
    cookielib.CookieJar support for webob.Response
    """
    def __init__(self, response):
        self._response = response

    def info(self):
        return self

    def getheaders(self, header):
        return self._response.headers.getall(header)

    def get_all(self, headers, default):  # NOQA
        # This is undocumented method that Python 3 cookielib uses
        return self._response.headers.getall(headers)


class URLMismatch:
    def __init__(self, message):
        self.messages = message if isinstance(message, list) else [message]

    def __bool__(self):
        return not bool(self.messages)

    def __repr__(self):
        return '\n'.join(self.messages)


class URL(str):
    '''
       string subclass with methods to extract or test parts of the URL
       structure.
    '''

    @functools.cached_property
    def request(self):
        '''Returns a :class:`webob.BaseRequest` object corresponding to this URL.'''
        parsed = urllib.parse.urlparse(self)
        request = webob.Request.blank(self)
        # XXX: webob force the http: scheme if parsed.scheme is absent XXX:
        # webob does not understand //{host}/ it interprets it as if //{host}/
        # is a path
        if not parsed.scheme:
            request.environ['PATH_INFO'] = parsed.path
            request.environ['HTTP_HOST'] = parsed.netloc
            request.environ['wsgi.url_scheme'] = None
        return request

    def __getattr__(self, attr):
        return getattr(self.request, attr)

    def join(self, other):
        '''Apply :meth:`urllib.parse.urljoin` and returns a new URL object.'''
        return URL(
            urllib.parse.urljoin(str(self), str(other) if other else ''))

    @property
    def netloc(self):
        '''netloc (host + port) of the URL.'''
        return urllib.parse.urlparse(self).netloc

    @property
    def host_url(self):
        '''returns :attr:`webob.BaseRequest.host_url` of the equivalent request.'''
        return URL(self.request.host_url)

    @property
    def path(self):
        '''returns :attr:`webob.BaseRequest.path` of the equivalent request.'''
        return URL(self.request.path)

    @property
    def path_url(self):
        '''returns :attr:`webob.BaseRequest.path_url` of the equivalent request.'''
        return URL(self.request.path_url)

    @property
    def path_qs(self):
        '''returns :attr:`webob.BaseRequest.path_qs` of the equivalent request.'''
        return URL(self.request.path_qs)

    def __repr__(self):
        return f'<{self.__class__.__name__} {str(self)!r}>'

    def match(self, other, strict=True):
        '''
           Returns True if `self` matches the `other` URL given as a string or
           an URL object.

           * scheme, netloc and path must be equal or missing
           * `/*/` can be used as a wildcard path

             >>> assert URL('https://example.com/foor/bar').match('https://example.com/*/')

           * in the query string, parameters must matches:

             >>> assert URL('//example.com/?foo=bar&bar=foo').loose_match('//example.com/?foo=bar')

           * but a parameter whose name starts with `!` must be absent (useful
             mainly for `loose_match()`)

             >>> assert URL('?foo=bar').loose_match('?!bar')

           * but a paramter whose value is `?` must have only one non empty
             value.

             >>> assert not URL('?foo=bar&foo=foo').match('https://example.com/?foo=?')

           * but a parameter whose value is `*` acccept any number of value or
             none, it's the wildcard match,

             >>> assert URL('?foo=bar&foo=foo').match('?foo=*')
        '''
        return self._match(other, strict=True)

    def loose_match(self, other):
        '''
            Match loosely against another URL. It's like `match()` but if a part of
            the URL is missing it will not returns False.
        '''
        return self._match(other, strict=False)


    def _match(self, other, strict=True):
        if not isinstance(other, URL):
            other = URL(other)
        errors = []
        if (strict or other.scheme) and other.scheme != self.scheme:
            errors.append(f'scheme differs {self.scheme} != {other.scheme}')
        if (strict or other.netloc) and self.netloc != other.netloc:
            errors.append(f'netloc differs {self.netloc} != {other.netloc}')
        if ((strict or other.path) and other.path != '/*/'
                and other.path != self.path):
            errors.append(f'path differs {self.path} != {other.path}')
        expected = set()
        if other.params:
            for key, value in other.params.items():
                # &!key forbids key in query string
                if key.startswith('!'):
                    if key[1:] in self.params:
                        qs = urllib.parse.urlencode(
                            [(key[1:], v) for v in self.params.getall(key[1:])])
                        errors.append(
                            f'{key[1:]} should be absent, but ?{qs} found.')
                elif value == '?':
                    values = self.params.getall(key)
                    if len(values) == 0 or (len(values) == 1 and not values[0]):
                        errors.append(
                            f'{key} should have only one value but is absent.')
                    elif len(values) > 1:
                        qs = urllib.parse.urlencode(
                            [(key, v) for v in self.params.getall(key)])
                        errors.append(
                            f'{key} should have only one value but ?{qs}'
                            ' found.')
                    else:
                        expected.add((key, self.params[key]))
                elif value == '*':
                    for v in self.params.getall(key):
                        expected.add((key, v))
                else:
                    if key not in self.params:
                        errors.append(
                            f'{key} should have value {value!r} but is absent.')
                    elif value not in self.params.getall(key):
                        qs = urllib.parse.urlencode(
                            [(key, v) for v in self.params.getall(key)])
                        errors.append(
                            f'{key} should have value {value!r} but'
                            f' ?{qs} found.')
                    else:
                        expected.add((key, value))

        if strict:
            for key, value in self.params.items():
                if (key, value) not in expected:
                    errors.append(f'?{key}={value} was not expected.')

        return URLMismatch(errors)
