# (c) 2005 Ian Bicking and contributors; written for Paste
# (http://pythonpaste.org)
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php
"""
Routines for testing WSGI applications.

Most interesting is TestApp
"""
from __future__ import unicode_literals

import cgi
import fnmatch
import mimetypes
import os
import random
import re
import warnings
from json import loads

from six import StringIO
from six import BytesIO
from six import string_types
from six import binary_type
from six import text_type
from six.moves import http_cookiejar

from webtest.compat import urlparse
from webtest.compat import print_stderr
from webtest.compat import urlencode
from webtest.compat import splittype
from webtest.compat import splithost
from webtest.compat import to_bytes
from webtest.compat import PY3
from webtest import forms
from webtest import lint
from webtest import utils

from bs4 import BeautifulSoup

import webob


__all__ = ['TestApp', 'TestRequest']


class RequestCookieAdapter(object):
    """
    this class merely provides the methods required for a
    cookielib.CookieJar to work on a webob.Request

    potential for yak shaving...very high
    """
    def __init__(self, request):
        self._request = request

    def is_unverifiable(self):
        return True  # sure? Why not?

    @property
    def unverifiable(self):  # NOQA
        # This is undocumented method that Python 3 cookielib uses
        return True

    def get_full_url(self):
        return self._request.url

    def get_origin_req_host(self):
        return self._request.host

    def add_unredirected_header(self, key, header):
        self._request.headers[key] = header

    def has_header(self, key):
        return key in self._request.headers


class ResponseCookieAdapter(object):
    """
    cookielib.CookieJar to work on a webob.Response
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


class AppError(Exception):

    def __init__(self, message, *args):
        if isinstance(message, binary_type):
            message = message.decode('utf8')
        str_args = ()
        for arg in args:
            if isinstance(arg, webob.Response):
                body = arg.body
                if isinstance(body, binary_type):
                    if arg.charset:
                        arg = body.decode(arg.charset)
                    else:
                        arg = repr(body)
            elif isinstance(arg, binary_type):
                try:
                    arg = arg.decode('utf8')
                except UnicodeDecodeError:
                    arg = repr(arg)
            str_args += (arg,)
        message = message % str_args
        Exception.__init__(self, message)


class TestResponse(webob.Response):

    """
    Instances of this class are return by ``TestApp``
    """

    request = None
    _forms_indexed = None

    @property
    def forms(self):
        """
        Returns a dictionary of :class:`~webtest.Form` objects.  Indexes are
        both in order (from zero) and by form id (if the form is given an id).
        """
        if self._forms_indexed is None:
            self._parse_forms()
        return self._forms_indexed

    @property
    def form(self):
        """Returns a single :class:`~webtest.Form` instance; it is an
        error if there are multiple forms on the page.
        """
        forms_ = self.forms
        if not forms_:
            raise TypeError(
                "You used response.form, but no forms exist")
        if 1 in forms_:
            # There is more than one form
            raise TypeError(
                "You used response.form, but more than one form exists")
        return forms_[0]

    @property
    def testbody(self):
        if self.charset:
            try:
                return self.text
            except UnicodeDecodeError:
                return self.body.decode(self.charset, 'replace')
        return self.body.decode('ascii', 'replace')

    _tag_re = re.compile(r'<(/?)([:a-z0-9_\-]*)(.*?)>', re.S | re.I)

    def _parse_forms(self):
        forms_ = self._forms_indexed = {}
        form_texts = [str(f) for f in self.html('form')]
        for i, text in enumerate(form_texts):
            form = forms.Form(self, text)
            forms_[i] = form
            if form.id:
                forms_[form.id] = form

    def follow(self, **kw):
        """
        If this request is a redirect, follow that redirect.  It
        is an error if this is not a redirect response.  Returns
        another response object.
        """
        assert self.status_int >= 300 and self.status_int < 400, (
            "You can only follow redirect responses (not %s)"
            % self.status)
        location = self.headers['location']
        type, rest = splittype(location)
        host, path = splithost(rest)
        # @@: We should test that it's not a remote redirect
        return self.test_app.get(location, **kw)

    def click(self, description=None, linkid=None, href=None,
              anchor=None, index=None, verbose=False,
              extra_environ=None):
        """
        Click the link as described.  Each of ``description``,
        ``linkid``, and ``url`` are *patterns*, meaning that they are
        either strings (regular expressions), compiled regular
        expressions (objects with a ``search`` method), or callables
        returning true or false.

        All the given patterns are ANDed together:

        * ``description`` is a pattern that matches the contents of the
          anchor (HTML and all -- everything between ``<a...>`` and
          ``</a>``)

        * ``linkid`` is a pattern that matches the ``id`` attribute of
          the anchor.  It will receive the empty string if no id is
          given.

        * ``href`` is a pattern that matches the ``href`` of the anchor;
          the literal content of that attribute, not the fully qualified
          attribute.

        * ``anchor`` is a pattern that matches the entire anchor, with
          its contents.

        If more than one link matches, then the ``index`` link is
        followed.  If ``index`` is not given and more than one link
        matches, or if no link matches, then ``IndexError`` will be
        raised.

        If you give ``verbose`` then messages will be printed about
        each link, and why it does or doesn't match.  If you use
        ``app.click(verbose=True)`` you'll see a list of all the
        links.

        You can use multiple criteria to essentially assert multiple
        aspects about the link, e.g., where the link's destination is.
        """
        found_html, found_desc, found_attrs = self._find_element(
            tag='a', href_attr='href',
            href_extract=None,
            content=description,
            id=linkid,
            href_pattern=href,
            html_pattern=anchor,
            index=index, verbose=verbose)
        return self.goto(str(found_attrs['uri']), extra_environ=extra_environ)

    def clickbutton(self, description=None, buttonid=None, href=None,
                    button=None, index=None, verbose=False):
        """
        Like ``.click()``, except looks for link-like buttons.
        This kind of button should look like
        ``<button onclick="...location.href='url'...">``.
        """
        found_html, found_desc, found_attrs = self._find_element(
            tag='button', href_attr='onclick',
            href_extract=re.compile(r"location\.href='(.*?)'"),
            content=description,
            id=buttonid,
            href_pattern=href,
            html_pattern=button,
            index=index, verbose=verbose)
        return self.goto(str(found_attrs['uri']))

    def _find_element(self, tag, href_attr, href_extract,
                      content, id,
                      href_pattern,
                      html_pattern,
                      index, verbose):
        content_pat = utils.make_pattern(content)
        id_pat = utils.make_pattern(id)
        href_pat = utils.make_pattern(href_pattern)
        html_pat = utils.make_pattern(html_pattern)

        body = self.testbody

        _tag_re = re.compile(r'<%s\s+(.*?)>(.*?)</%s>' % (tag, tag),
                             re.I + re.S)
        _script_re = re.compile(r'<script.*?>.*?</script>', re.I | re.S)
        bad_spans = []
        for match in _script_re.finditer(body):
            bad_spans.append((match.start(), match.end()))

        def printlog(s):
            if verbose:
                print(s)

        found_links = []
        total_links = 0
        for match in _tag_re.finditer(body):
            found_bad = False
            for bad_start, bad_end in bad_spans:
                if (match.start() > bad_start
                    and match.end() < bad_end):
                    found_bad = True
                    break
            if found_bad:
                continue
            el_html = match.group(0)
            el_attr = match.group(1)
            el_content = match.group(2)
            attrs = utils.parse_attrs(el_attr)
            if verbose:
                printlog('Element: %r' % el_html)
            if not attrs.get(href_attr):
                printlog('  Skipped: no %s attribute' % href_attr)
                continue
            el_href = attrs[href_attr]
            if href_extract:
                m = href_extract.search(el_href)
                if not m:
                    printlog("  Skipped: doesn't match extract pattern")
                    continue
                el_href = m.group(1)
            attrs['uri'] = el_href
            if el_href.startswith('#'):
                printlog('  Skipped: only internal fragment href')
                continue
            if el_href.startswith('javascript:'):
                printlog('  Skipped: cannot follow javascript:')
                continue
            total_links += 1
            if content_pat and not content_pat(el_content):
                printlog("  Skipped: doesn't match description")
                continue
            if id_pat and not id_pat(attrs.get('id', '')):
                printlog("  Skipped: doesn't match id")
                continue
            if href_pat and not href_pat(el_href):
                printlog("  Skipped: doesn't match href")
                continue
            if html_pat and not html_pat(el_html):
                printlog("  Skipped: doesn't match html")
                continue
            printlog("  Accepted")
            found_links.append((el_html, el_content, attrs))
        if not found_links:
            raise IndexError(
                "No matching elements found (from %s possible)"
                % total_links)
        if index is None:
            if len(found_links) > 1:
                raise IndexError(
                    "Multiple links match: %s"
                    % ', '.join([repr(anc) for anc, d, attr in found_links]))
            found_link = found_links[0]
        else:
            try:
                found_link = found_links[index]
            except IndexError:
                raise IndexError(
                    "Only %s (out of %s) links match; index %s out of range"
                    % (len(found_links), total_links, index))
        return found_link

    def goto(self, href, method='get', **args):
        """
        Go to the (potentially relative) link ``href``, using the
        given method (``'get'`` or ``'post'``) and any extra arguments
        you want to pass to the ``app.get()`` or ``app.post()``
        methods.

        All hostnames and schemes will be ignored.
        """
        scheme, host, path, query, fragment = urlparse.urlsplit(href)
        # We
        scheme = host = fragment = ''
        href = urlparse.urlunsplit((scheme, host, path, query, fragment))
        href = urlparse.urljoin(self.request.url, href)
        method = method.lower()
        assert method in ('get', 'post'), (
            'Only "get" or "post" are allowed for method (you gave %r)'
            % method)

        # encode unicode strings for the outside world
        if not PY3 and getattr(self, '_use_unicode', False):
            def to_str(s):
                if isinstance(s, text_type):
                    return s.encode(self.charset)
                return s

            href = to_str(href)

            if 'params' in args:
                args['params'] = [tuple(map(to_str, p))
                                  for p in args['params']]

            if 'upload_files' in args:
                args['upload_files'] = [map(to_str, f)
                                        for f in args['upload_files']]

            if 'content_type' in args:
                args['content_type'] = to_str(args['content_type'])

        if method == 'get':
            method = self.test_app.get
        else:
            method = self.test_app.post
        return method(href, **args)

    _normal_body_regex = re.compile(to_bytes(r'[ \n\r\t]+'))

    _normal_body = None

    def normal_body__get(self):
        if self._normal_body is None:
            self._normal_body = self._normal_body_regex.sub(
                                                b' ', self.body)
        return self._normal_body

    normal_body = property(normal_body__get,
                           doc="""
                           Return the whitespace-normalized body
                           """.strip())

    _unicode_normal_body_regex = re.compile('[ \\n\\r\\t]+')

    _unicode_normal_body = None

    def unicode_normal_body__get(self):
        if not self.charset:
            raise AttributeError(
                ("You cannot access Response.unicode_normal_body "
                 "unless charset is set"))
        if self._unicode_normal_body is None:
            self._unicode_normal_body = self._unicode_normal_body_regex.sub(
                                                ' ', self.testbody)
        return self._unicode_normal_body

    unicode_normal_body = property(
        unicode_normal_body__get, doc="""
        Return the whitespace-normalized body, as unicode
        """.strip())

    def __contains__(self, s):
        """
        A response 'contains' a string if it is present in the body
        of the response.  Whitespace is normalized when searching
        for a string.
        """
        if not self.charset and isinstance(s, text_type):
            s = s.encode('utf8')
        if isinstance(s, binary_type):
            return s in self.body or s in self.normal_body
        return s in self.testbody or s in self.unicode_normal_body

    def mustcontain(self, *strings, **kw):
        """
        Assert that the response contains all of the strings passed
        in as arguments.

        Equivalent to::

            assert string in res
        """
        if 'no' in kw:
            no = kw['no']
            del kw['no']
            if isinstance(no, string_types):
                no = [no]
        else:
            no = []
        if kw:
            raise TypeError(
                "The only keyword argument allowed is 'no'")
        for s in strings:
            if not s in self:
                print_stderr("Actual response (no %r):" % s)
                print_stderr(str(self))
                raise IndexError(
                    "Body does not contain string %r" % s)
        for no_s in no:
            if no_s in self:
                print_stderr("Actual response (has %r)" % no_s)
                print_stderr(str(self))
                raise IndexError(
                    "Body contains bad string %r" % no_s)

    def __str__(self):
        simple_body = str('\n').join([l for l in self.testbody.splitlines()
                                     if l.strip()])
        headers = [(n.title(), v)
                   for n, v in self.headerlist
                   if n.lower() != 'content-length']
        headers.sort()
        output = str('Response: %s\n%s\n%s') % (
            self.status,
            str('\n').join([str('%s: %s') % (n, v) for n, v in headers]),
            simple_body)
        if not PY3 and isinstance(output, text_type):
            output = output.encode(self.charset or 'utf8', 'replace')
        return output

    def __unicode__(self):
        output = str(self)
        if PY3:
            return output
        return output.decode(self.charset or 'utf8', 'replace')

    def __repr__(self):
        # Specifically intended for doctests
        if self.content_type:
            ct = ' %s' % self.content_type
        else:
            ct = ''
        if self.body:
            br = repr(self.body)
            if len(br) > 18:
                br = br[:10] + '...' + br[-5:]
                br += '/%s' % len(self.body)
            body = ' body=%s' % br
        else:
            body = ' no body'
        if self.location:
            location = ' location: %s' % self.location
        else:
            location = ''
        return ('<' + self.status + ct + location + body + '>')

    def html(self):
        """
        Returns the response as a `BeautifulSoup
        <http://www.crummy.com/software/BeautifulSoup/documentation.html>`_
        object.

        Only works with HTML responses; other content-types raise
        AttributeError.
        """
        if 'html' not in self.content_type:
            raise AttributeError(
                "Not an HTML response body (content-type: %s)"
                % self.content_type)
        soup = BeautifulSoup(self.testbody)
        return soup

    html = property(html, doc=html.__doc__)

    def xml(self):
        """
        Returns the response as an `ElementTree
        <http://python.org/doc/current/lib/module-xml.etree.ElementTree.html>`_
        object.

        Only works with XML responses; other content-types raise
        AttributeError
        """
        if 'xml' not in self.content_type:
            raise AttributeError(
                "Not an XML response body (content-type: %s)"
                % self.content_type)
        try:
            from xml.etree import ElementTree
        except ImportError:
            try:
                import ElementTree
            except ImportError:
                try:
                    from elementtree import ElementTree  # NOQA
                except ImportError:
                    raise ImportError(
                        ("You must have ElementTree installed "
                         "(or use Python 2.5) to use response.xml"))
        # ElementTree can't parse unicode => use `body` instead of `testbody`
        return ElementTree.XML(self.body)

    xml = property(xml, doc=xml.__doc__)

    def lxml(self):
        """
        Returns the response as an `lxml object
        <http://codespeak.net/lxml/>`_.  You must have lxml installed
        to use this.

        If this is an HTML response and you have lxml 2.x installed,
        then an ``lxml.html.HTML`` object will be returned; if you
        have an earlier version of lxml then a ``lxml.HTML`` object
        will be returned.
        """
        if ('html' not in self.content_type
            and 'xml' not in self.content_type):
            raise AttributeError(
                "Not an XML or HTML response body (content-type: %s)"
                % self.content_type)
        try:
            from lxml import etree
        except ImportError:
            raise ImportError(
                "You must have lxml installed to use response.lxml")
        try:
            from lxml.html import fromstring
        except ImportError:
            fromstring = etree.HTML
        ## FIXME: would be nice to set xml:base, in some fashion
        if self.content_type == 'text/html':
            return fromstring(self.testbody, base_url=self.request.url)
        else:
            return etree.XML(self.testbody, base_url=self.request.url)

    lxml = property(lxml, doc=lxml.__doc__)

    def json(self):
        """
        Return the response as a JSON response.  You must have `simplejson
        <http://goo.gl/B9g6s>`_ installed to use this, or be using a Python
        version with the json module.

        The content type must be application/json to use this.
        """
        if self.content_type != 'application/json':
            raise AttributeError(
                "Not a JSON response body (content-type: %s)"
                % self.content_type)
        return loads(self.testbody)

    json = property(json, doc=json.__doc__)

    def pyquery(self):
        """
        Returns the response as a `PyQuery <http://pyquery.org/>`_ object.

        Only works with HTML and XML responses; other content-types raise
        AttributeError.
        """
        if 'html' not in self.content_type and 'xml' not in self.content_type:
            raise AttributeError(
                "Not an HTML or XML response body (content-type: %s)"
                % self.content_type)
        try:
            from pyquery import PyQuery
        except ImportError:
            raise ImportError(
                "You must have PyQuery installed to use response.pyquery")
        d = PyQuery(self.testbody)
        return d

    pyquery = property(pyquery, doc=pyquery.__doc__)

    def showbrowser(self):
        """
        Show this response in a browser window (for debugging purposes,
        when it's hard to read the HTML).
        """
        import webbrowser
        import tempfile
        f = tempfile.NamedTemporaryFile(prefix='webtest-page',
                                        suffix='.html')
        name = f.name
        f.close()
        f = open(name, 'w')
        if PY3:
            f.write(self.body.decode(self.charset or 'ascii', 'replace'))
        else:
            f.write(self.body)
        f.close()
        if name[0] != '/':
            # windows ...
            url = 'file:///' + name
        else:
            url = 'file://' + name
        webbrowser.open_new(url)


class TestRequest(webob.Request):
    ResponseClass = TestResponse


class TestApp(object):
    """
    Wraps a WSGI application in a more convenient interface for
    testing.

    ``app`` may be an application, or a Paste Deploy app
    URI, like ``'config:filename.ini#test'``.

    ``extra_environ`` is a dictionary of values that should go
    into the environment for each request.  These can provide a
    communication channel with the application.

    ``relative_to`` is a directory, and filenames used for file
    uploads are calculated relative to this.  Also ``config:``
    URIs that aren't absolute.

    ``cookiejar`` is a `cookielib.CookieJar` instance that keeps cookies
    across requets. See official Python documentation for the API.

    ``cookies`` is a convenient shortcut for a dict of all cookies in
    ``cookiejar``.

    """

    RequestClass = TestRequest

    def __init__(self, app, extra_environ=None, relative_to=None,
                 use_unicode=True):
        if isinstance(app, string_types):
            from paste.deploy import loadapp
            # @@: Should pick up relative_to from calling module's
            # __file__
            app = loadapp(app, relative_to=relative_to)
        self.app = app
        self.relative_to = relative_to
        if extra_environ is None:
            extra_environ = {}
        self.extra_environ = extra_environ
        self.use_unicode = use_unicode
        self.cookiejar = http_cookiejar.CookieJar()

    @property
    def cookies(self):
        return dict([(cookie.name, cookie) for cookie in self.cookiejar])

    def reset(self):
        """
        Resets the state of the application; currently just clears
        saved cookies.
        """
        self.cookiejar.clear()

    def _make_environ(self, extra_environ=None):
        environ = self.extra_environ.copy()
        environ['paste.throw_errors'] = True
        if extra_environ:
            environ.update(extra_environ)
        return environ

    def _remove_fragment(self, url):
        scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
        return urlparse.urlunsplit((scheme, netloc, path, query, ""))

    def get(self, url, params=None, headers=None, extra_environ=None,
            status=None, expect_errors=False):
        """
        Get the given url (well, actually a path like
        ``'/page.html'``).

        ``params``:
            A query string, or a dictionary that will be encoded
            into a query string.  You may also include a query
            string on the ``url``.

        ``headers``:
            A dictionary of extra headers to send.

        ``extra_environ``:
            A dictionary of environmental variables that should
            be added to the request.

        ``status``:
            The integer status code you expect (if not 200 or 3xx).
            If you expect a 404 response, for instance, you must give
            ``status=404`` or it will be an error.  You can also give
            a wildcard, like ``'3*'`` or ``'*'``.

        ``expect_errors``:
            If this is not true, then if anything is written to
            ``wsgi.errors`` it will be an error.  If it is true, then
            non-200/3xx responses are also okay.

        Returns a :class:`webtest.TestResponse` object.
        """
        environ = self._make_environ(extra_environ)
        url = str(url)
        url = self._remove_fragment(url)
        if params:
            if not isinstance(params, string_types):
                params = urlencode(params, doseq=True)
            if str('?') in url:
                url += str('&')
            else:
                url += str('?')
            url += params
        if str('?') in url:
            url, environ['QUERY_STRING'] = url.split(str('?'), 1)
        else:
            environ['QUERY_STRING'] = str('')
        req = self.RequestClass.blank(url, environ)
        if headers:
            req.headers.update(headers)
        return self.do_request(req, status=status,
                               expect_errors=expect_errors)

    def _gen_request(self, method, url, params=utils.NoDefault, headers=None,
                     extra_environ=None, status=None, upload_files=None,
                     expect_errors=False, content_type=None):
        """
        Do a generic request.
        """

        if method == 'DELETE' and params is not utils.NoDefault:
            warnings.warn(('You are not supposed to send a body in a '
                           'DELETE request. Most web servers will ignore it'),
                           lint.WSGIWarning)

        environ = self._make_environ(extra_environ)

        inline_uploads = []

        # this supports OrderedDict
        if isinstance(params, dict) or hasattr(params, 'items'):
            params = list(params.items())

        if isinstance(params, (list, tuple)):
            inline_uploads = [v for (k, v) in params
                              if isinstance(v, (forms.File, forms.Upload))]

        if len(inline_uploads) > 0:
            content_type, params = self.encode_multipart(
                params, upload_files or ())
            environ['CONTENT_TYPE'] = content_type
        else:
            params = utils.encode_params(params, content_type)
            if upload_files or \
                (content_type and
                 to_bytes(content_type).startswith(b'multipart')):
                params = cgi.parse_qsl(params, keep_blank_values=True)
                content_type, params = self.encode_multipart(
                    params, upload_files or ())
                environ['CONTENT_TYPE'] = content_type
            elif params:
                environ.setdefault('CONTENT_TYPE',
                                   str('application/x-www-form-urlencoded'))

        if content_type is not None:
            environ['CONTENT_TYPE'] = content_type
        environ['REQUEST_METHOD'] = str(method)
        url = str(url)
        url = self._remove_fragment(url)
        req = self.RequestClass.blank(url, environ)
        if isinstance(params, text_type):
            params = params.encode(req.charset or 'utf8')
        req.environ['wsgi.input'] = BytesIO(params)
        req.content_length = len(params)
        if headers:
            req.headers.update(headers)
        return self.do_request(req, status=status,
                               expect_errors=expect_errors)

    def post(self, url, params='', headers=None, extra_environ=None,
             status=None, upload_files=None, expect_errors=False,
             content_type=None):
        """
        Do a POST request.  Very like the ``.get()`` method.
        ``params`` are put in the body of the request.

        ``upload_files`` is for file uploads.  It should be a list of
        ``[(fieldname, filename, file_content)]``.  You can also use
        just ``[(fieldname, filename)]`` and the file content will be
        read from disk.

        For post requests params could be a collections.OrderedDict with
        Upload fields included in order:

            app.post('/myurl', collections.OrderedDict([
                ('textfield1', 'value1'),
                ('uploadfield', webapp.Upload('filename.txt', 'contents'),
                ('textfield2', 'value2')])))

        Returns a ``webob.Response`` object.
        """
        return self._gen_request('POST', url, params=params, headers=headers,
                                 extra_environ=extra_environ, status=status,
                                 upload_files=upload_files,
                                 expect_errors=expect_errors,
                                 content_type=content_type,
                                 )

    def put(self, url, params='', headers=None, extra_environ=None,
            status=None, upload_files=None, expect_errors=False,
            content_type=None):
        """
        Do a PUT request.  Very like the ``.post()`` method.
        ``params`` are put in the body of the request, if params is a
        tuple, dictionary, list, or iterator it will be urlencoded and
        placed in the body as with a POST, if it is string it will not
        be encoded, but placed in the body directly.

        Returns a ``webob.Response`` object.
        """
        return self._gen_request('PUT', url, params=params, headers=headers,
                                 extra_environ=extra_environ, status=status,
                                 upload_files=upload_files,
                                 expect_errors=expect_errors,
                                 content_type=content_type,
                                 )

    def patch(self, url, params='', headers=None, extra_environ=None,
              status=None, upload_files=None, expect_errors=False,
              content_type=None):
        """
        Do a PATCH request.  Very like the ``.post()`` method.
        ``params`` are put in the body of the request, if params is a
        tuple, dictionary, list, or iterator it will be urlencoded and
        placed in the body as with a POST, if it is string it will not
        be encoded, but placed in the body directly.

        Returns a ``webob.Response`` object.
        """
        return self._gen_request('PATCH', url, params=params, headers=headers,
                                 extra_environ=extra_environ, status=status,
                                 upload_files=upload_files,
                                 expect_errors=expect_errors,
                                 content_type=content_type,
                                 )

    def delete(self, url, params='', headers=None, extra_environ=None,
               status=None, expect_errors=False, content_type=None):
        """
        Do a DELETE request.  Very like the ``.get()`` method.

        Returns a ``webob.Response`` object.
        """
        return self._gen_request('DELETE', url, params=params, headers=headers,
                                 extra_environ=extra_environ, status=status,
                                 upload_files=None,
                                 expect_errors=expect_errors,
                                 content_type=content_type,
                                 )

    def options(self, url, headers=None, extra_environ=None,
                status=None, expect_errors=False):
        """
        Do a OPTIONS request.  Very like the ``.get()`` method.

        Returns a ``webob.Response`` object.
        """
        return self._gen_request('OPTIONS', url, headers=headers,
                                 extra_environ=extra_environ, status=status,
                                 upload_files=None,
                                 expect_errors=expect_errors,
                                 )

    def head(self, url, headers=None, extra_environ=None,
             status=None, expect_errors=False):
        """
        Do a HEAD request.  Very like the ``.get()`` method.

        Returns a ``webob.Response`` object.
        """
        return self._gen_request('HEAD', url, headers=headers,
                                 extra_environ=extra_environ, status=status,
                                 upload_files=None,
                                 expect_errors=expect_errors,
                                 )

    post_json = utils.json_method('POST')
    put_json = utils.json_method('PUT')
    patch_json = utils.json_method('PATCH')
    delete_json = utils.json_method('DELETE')

    def encode_multipart(self, params, files):
        """
        Encodes a set of parameters (typically a name/value list) and
        a set of files (a list of (name, filename, file_body)) into a
        typical POST body, returning the (content_type, body).
        """
        boundary = to_bytes(str(random.random()))[2:]
        boundary = b'----------a_BoUnDaRy' + boundary + b'$'
        lines = []

        def _append_file(file_info):
            key, filename, value = self._get_file_info(file_info)
            if isinstance(filename, text_type):
                fcontent = mimetypes.guess_type(filename)[0]
                try:
                    filename = filename.encode('utf8')
                except:
                    raise  # file names must be ascii
            else:
                fcontent = mimetypes.guess_type(filename.decode('ascii'))[0]
            if isinstance(value, text_type):
                try:
                    value = value.encode('ascii')
                except:
                    raise TypeError(
                            'You are trying to upload some non ascii content.'
                            'Please encode it first')
            fcontent = to_bytes(fcontent)
            fcontent = fcontent or b'application/octet-stream'
            lines.extend([
                b'--' + boundary,
                b'Content-Disposition: form-data; ' + \
                b'name="' + key + b'"; filename="' + filename + b'"',
                b'Content-Type: ' + fcontent, b'', value])

        for key, value in params:
            if isinstance(key, text_type):
                try:
                    key = key.encode('ascii')
                except:
                    raise  # field name are always ascii
            if isinstance(value, forms.File):
                if value.value:
                    _append_file([key] + list(value.value))
            elif isinstance(value, forms.Upload):
                file_info = [key, value.filename]
                if value.content is not None:
                    file_info.append(value.content)
                _append_file(file_info)
            else:
                if isinstance(value, text_type):
                    value = value.encode('utf8')
                lines.extend([
                    b'--' + boundary,
                    b'Content-Disposition: form-data; name="' + key + b'"',
                    b'', value])

        for file_info in files:
            _append_file(file_info)

        lines.extend([b'--' + boundary + b'--', b''])
        body = b'\r\n'.join(lines)
        boundary = boundary.decode('ascii')
        content_type = 'multipart/form-data; boundary=%s' % boundary
        return content_type, body

    def _get_file_info(self, file_info):
        if len(file_info) == 2:
            # It only has a filename
            filename = file_info[1]
            if self.relative_to:
                filename = os.path.join(self.relative_to, filename)
            f = open(filename, 'rb')
            content = f.read()
            if PY3 and isinstance(content, text_type):
                # we want bytes
                content = content.encode(f.encoding)
            f.close()
            return (file_info[0], filename, content)
        elif len(file_info) == 3:
            content = file_info[2]
            if not isinstance(content, binary_type):
                raise ValueError('File content must be %s not %s'
                                 % (binary_type, type(content)))
            return file_info
        else:
            raise ValueError(
                "upload_files need to be a list of tuples of (fieldname, "
                "filename, filecontent) or (fieldname, filename); "
                "you gave: %r"
                % repr(file_info)[:100])

    def request(self, url_or_req, status=None, expect_errors=False,
                **req_params):
        """
        Creates and executes a request.  You may either pass in an
        instantiated :class:`TestRequest` object, or you may pass in a
        URL and keyword arguments to be passed to
        :meth:`TestRequest.blank`.

        You can use this to run a request without the intermediary
        functioning of :meth:`TestApp.get` etc.  For instance, to
        test a WebDAV method::

            resp = app.request('/new-col', method='MKCOL')

        Note that the request won't have a body unless you specify it,
        like::

            resp = app.request('/test.txt', method='PUT', body='test')

        You can use ``POST={args}`` to set the request body to the
        serialized arguments, and simultaneously set the request
        method to ``POST``
        """
        if isinstance(url_or_req, text_type):
            url_or_req = str(url_or_req)
        for (k, v) in req_params.items():
            if isinstance(v, text_type):
                req_params[k] = str(v)
        if isinstance(url_or_req, string_types):
            req = self.RequestClass.blank(url_or_req, **req_params)
        else:
            req = url_or_req.copy()
            for name, value in req_params.items():
                setattr(req, name, value)
            if req.content_length == -1:
                req.content_length = len(req.body)
        req.environ['paste.throw_errors'] = True
        for name, value in self.extra_environ.items():
            req.environ.setdefault(name, value)
        return self.do_request(req,
                               status=status,
                               expect_errors=expect_errors,
                               )

    def do_request(self, req, status, expect_errors):
        """
        Executes the given request (``req``), with the expected
        ``status``.  Generally ``.get()`` and ``.post()`` are used
        instead.

        To use this::

            resp = app.do_request(webtest.TestRequest.blank(
                'url', ...args...))

        Note you can pass any keyword arguments to
        ``TestRequest.blank()``, which will be set on the request.
        These can be arguments like ``content_type``, ``accept``, etc.
        """

        errors = StringIO()
        req.environ['wsgi.errors'] = errors
        script_name = req.environ.get('SCRIPT_NAME', '')
        if script_name and req.path_info.startswith(script_name):
            req.path_info = req.path_info[len(script_name):]

        req.environ['paste.testing'] = True
        req.environ['paste.testing_variables'] = {}

        # verify wsgi compatibility
        app = lint.middleware(self.app)

        ## FIXME: should it be an option to not catch exc_info?
        res = req.get_response(app, catch_exc_info=True)
        # set a few handy attributes
        res._use_unicode = self.use_unicode
        res.request = req
        res.app = app
        res.test_app = self

        # We do this to make sure the app_iter is exausted:
        try:
            res.body
        except TypeError:
            pass
        res.errors = errors.getvalue()

        for name, value in req.environ['paste.testing_variables'].items():
            if hasattr(res, name):
                raise ValueError(
                    "paste.testing_variables contains the variable %r, but "
                    "the response object already has an attribute by that "
                    "name" % name)
            setattr(res, name, value)
        if not expect_errors:
            self._check_status(status, res)
            self._check_errors(res)

        # merge cookies back in
        self.cookiejar.extract_cookies(ResponseCookieAdapter(res),
                                        RequestCookieAdapter(req))

        return res

    def _check_status(self, status, res):
        if status == '*':
            return
        res_status = res.status
        if (isinstance(status, string_types)
            and '*' in status):
            if re.match(fnmatch.translate(status), res_status, re.I):
                return
        if isinstance(status, (list, tuple)):
            if res.status_int not in status:
                raise AppError(
                    "Bad response: %s (not one of %s for %s)\n%s",
                    res_status, ', '.join(map(str, status)),
                    res.request.url, res)
            return
        if status is None:
            if res.status_int >= 200 and res.status_int < 400:
                return
            raise AppError(
                "Bad response: %s (not 200 OK or 3xx redirect for %s)\n%s",
                res_status, res.request.url,
                res)
        if status != res.status_int:
            raise AppError(
                "Bad response: %s (not %s)", res_status, status)

    def _check_errors(self, res):
        errors = res.errors
        if errors:
            raise AppError(
                "Application had errors logged:\n%s", errors)
