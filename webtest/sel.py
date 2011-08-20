# (c) 2005 Ian Bicking and contributors; written for Paste (http://pythonpaste.org)
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
"""
Routines for testing WSGI applications with selenium.

Most interesting is SeleniumApp
"""
import os
import cgi
import sys
import time
import urllib
import signal
import socket
import webob
import httplib
import logging
import warnings
import threading
from functools import wraps
from webtest import testapp
from wsgiref import simple_server

try:
    import json
except ImportError:
    import simplejson as json

class SeleniumWarning(Warning):
    pass

try:
    from selenium import selenium as browser
    def start(self, *browserConfigurationOptions):
        start_args = [self.browserStartCommand, self.browserURL, self.extensionJs]
        if browserConfigurationOptions:
          start_args.extend(browserConfigurationOptions)
        result = self.get_string("getNewBrowserSession", start_args)
        try:
            self.sessionId = result
        except ValueError:
            raise Exception, result
    browser.start = start
except ImportError:
    warnings.warn('selenium module is not available', SeleniumWarning)
    browser = False

logger = logging.getLogger('nose')

def log(*args):
    logger.error(*args)

class WSGIApplication(object):
    """A WSGI middleware to handle special calls used to run a test app"""

    def __init__(self, app, port):
        self.app = app
        self.serve_forever = True
        self.port = port
        self.url = 'http://127.0.0.1:%s/' % port
        self.thread = None

    def __call__(self, environ, start_response):
        if '__kill_application__' in environ['PATH_INFO']:
            self.serve_forever = False
            resp = webob.Response()
            return resp(environ, start_response)
        elif '__application__' in environ['PATH_INFO']:
            resp = webob.Response()
            resp.body = 'Application running'
            return resp(environ, start_response)
        return self.app(environ, start_response)

    def __repr__(self):
        return '<WSGIApplication %r at %s>' % (self.app, self.url)

class WSGIServer(simple_server.WSGIServer):
    """A WSGIServer"""

    def serve_forever(self):
        while self.application.serve_forever:
            self.handle_request()

def is_selenium_available(host='127.0.0.1', port=4444, **kwargs):
    """return True if the selenium module is available and a RC server is
    running"""
    if not browser:
        return False
    try:
        conn = httplib.HTTPConnection(host, port)
        conn.request('GET', '/')
    except socket.error:
        return False
    return True

def with_selenium(commands=(), host='127.0.0.1', port=4444, close=True):
    """A decorator to run tests only when selenium is available"""
    if not commands:
        commands = ('*chrome',)
    def wrapped(func_or_class):
        if is_selenium_available(host=host, port=port):
            if isinstance(func_or_class, type):
                return func_or_class
            else:
                @wraps(func_or_class)
                def wrapper(self):
                        old_app = self.app
                        for command in commands:
                            self.app = SeleniumApp(self.app.app, command=command,
                                                   host=host, port=port)
                            try:
                                res = func_or_class(self)
                            finally:
                                if close:
                                    self.app.close()
                        self.app = old_app
                return wrapper
    return wrapped

class SeleniumApp(testapp.TestApp):
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
    """

    apps = []

    def __init__(self, app=None, url=None,
                 host='localhost', port=4444,
                 command='*chrome', timeout=4000,
                 extra_environ=None, relative_to=None, **kwargs):
        self.app = None
        if app:
            super(SeleniumApp, self).__init__(app, relative_to=relative_to)
            self._run_server(self.app)
            url = self.app.url
        self.sel = browser(host, port, command, url)
        self.sel.start("captureNetworkTraffic=true", "addCustomRequestHeader=true")
        self.extra_environ = extra_environ or {}
        self.timeout = timeout
        self.testapp = self

    def get(self, url, params=None, extra_environ=None, timeout=None):
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

        Returns a :class:`webtest.sel.TestResponse` object.
        """
        self._make_environ(extra_environ)
        url = self._remove_fragment(url)
        if params:
            if not isinstance(params, (str, unicode)):
                params = urllib.urlencode(params, doseq=True)
            if '?' in url:
                url += '&'
            else:
                url += '?'
            url += params
        url = str(url)
        self.sel.open(url)
        return self._get_response(timeout=timeout)

    def post(self, *args, **kwargs):
        raise NotImplementedError()

    request = put = delete = post

    def _make_environ(self, extra_environ):
        self.sel.capture_network_traffic(type='json')
        environ = self.testapp.extra_environ.copy()
        if extra_environ:
            environ.update(extra_environ)
        for h, v in environ.items():
            if h.startswith('HTTP_'):
                h = h.split('_', 1)[1].replace('_', '-').title()
                self.sel.do_command('addCustomRequestHeader', [h, v])

    def _get_response(self, resp=None, timeout=None):
        if timeout != 0:
            timeout = timeout or self.timeout
            self.sel.wait_for_page_to_load(timeout)
        trafic = json.loads(self.sel.capture_network_traffic(type='json'))
        body = self.sel.get_string('getHtmlSource', [])
        responses = []
        for d in trafic:
            if d['url'].endswith('.ico'):
                continue
            req = webob.Request.blank(d['url'])
            for h in d['requestHeaders']:
                req.headers[h['name']] = h['value']
            resp = TestResponse(self.testapp, stack=responses)
            resp.status = str(d['statusCode'])
            for h in d['responseHeaders']:
                resp.headers[h['name']] = h['value']
            if resp.status_int == 200 and 'text/' in resp.content_type:
                if not resp.charset:
                    resp.charset = 'utf-8'
                resp.unicode_body = body
            responses.append(resp)
        if responses:
            return responses.pop(0)
        elif resp is not None:
            resp.unicode_body = body
            return resp
        else:
            raise AssertionError('No response found')

    def _run_server(self, app):
        s = socket.socket()
        s.bind(('', 0))
        ip, port = s.getsockname()
        s.close()
        self.app = app = WSGIApplication(app, port)
        def run():
            httpd = simple_server.make_server('127.0.0.1', port, app,
                                              server_class=WSGIServer)
            httpd.serve_forever()
        app.thread = threading.Thread(target=run)
        app.thread.start()
        conn = httplib.HTTPConnection("127.0.0.1", port)
        while True:
            try:
                conn.request('GET', '/__application__')
            except (socket.error, httplib.CannotSendRequest), e:
                time.sleep(.1)
            else:
                resp = conn.getresponse()
                break

    def close(self):
        self.sel.stop()
        if self.app:
            conn = httplib.HTTPConnection("127.0.0.1", self.app.port)
            while True:
                try:
                    conn.request('GET', '/__kill_application__')
                    resp = conn.getresponse()
                except socket.error:
                    self.app.thread.join()
                    break


class TestResponse(testapp.TestResponse):

    def __init__(self, app, stack):
        super(TestResponse, self).__init__()
        self.testapp = app
        self.sel = app.sel
        self.stack = stack

    def follow(self, **kw):
        """
        If this request is a redirect, follow that redirect.  It
        is an error if this is not a redirect response.  Returns
        another response object.
        """
        if self.status_int not in (301, 302):
            raise AssertionError('You can only follow 301 and 302. Not %s' % self.status_int)
        return self.stack.pop(0)

    def click(self, description=None, linkid=None, href=None,
              anchor=None, index=None, xpath=None, verbose=False,
              extra_environ=None, timeout=None):
        """
        Click the link as described.  Each of ``description``,
        ``linkid``, and ``url`` are *patterns*, meaning that they are
        either strings (regular expressions), compiled regular
        expressions (objects with a ``search`` method), or callables
        returning true or false.

        You can only use one patter:

        * ``description`` is a pattern that matches the contents of the
          anchor (HTML and all -- everything between ``<a...>`` and
          ``</a>``)

        * ``linkid`` is a pattern that matches the ``id`` attribute of
          the anchor.  It will receive the empty string if no id is
          given.

        * ``href`` is a pattern that matches the ``href`` of the anchor;
          the literal content of that attribute, not the fully qualified
          attribute.

        * ``xpath`` is a valid selenium xpath.

        """
        if description:
            locator = "xpath=//a[text()='%s']" % description
        elif xpath:
            locator = "xpath=%s" % xpath
        elif linkid:
            locator = "xpath=//a[@id='%s']" % linkid
        elif href:
            locator = "xpath=//a[@href='%s']" % href
        elif locator:
            locator = locator
        else:
            raise ValueError('You must provide a selector')
        self.testapp._make_environ(extra_environ)
        self.sel.click(locator)
        return self.testapp._get_response(resp=self, timeout=timeout)

    @property
    def forms(self):
        return Forms(self)

    @property
    def form(self):
        return Form(self, 0)

    def __repr__(self):
        return webob.Response.__repr__(self)

class Forms(object):

    def __init__(self, resp):
        self.resp = resp

    def __getitem__(self, key):
        return Form(self.resp, key)

class Field(testapp.Field):
    classes = {}

    def __init__(self, *args, **kwargs):
        super(Field, self).__init__(*args, **kwargs)
        self.sel = self.form.sel
        self.options = []
        self.selectedIndices = []
        self._forced_values = []
        if self.name:
            attr = 'name'
            value = self.name
        elif self.id:
            attr = 'id'
            value = self.id
        self.locator = '%s//%s[@%s="%s"]' % (self.form.locator, self.tag, attr, value)

    def value__set(self, value):
        if not self.settable:
            raise AttributeError(
                "You cannot set the value of the <%s> field %r"
                % (self.tag, self.name))
        self.form.sel.type(self.locator, value)

    def value__get(self):
        return self.form.sel.get_value.sel.type(self.locator, value)

    value = property(value__get, value__set)

class Select(Field):

    """
    Field representing ``<select>``
    """

    def force_value(self, value):
        self.form.sel.select(self.locator, 'value=%s' % value)

    def value__set(self, value):
        self.form.sel.select(self.locator, 'value=%s' % value)

    def value__get(self):
        return self.form.sel.get_selected_value(self.locator)

    value = property(value__get, value__set)

Field.classes['select'] = Select

class MultipleSelect(Field):

    """
    Field representing ``<select multiple="multiple">``
    """

    def force_value(self, values):
        self.form.sel.remove_all_selections(self.locator)
        for v in values:
            self.form.sel.select(self.locator, 'value=%s' % v)

    def value__set(self, values):
        self.form.sel.remove_all_selections(self.locator)
        str_values = [testapp._stringify(value) for value in values]
        for v in str_values:
            self.form.sel.add_selection(self.locator, 'value=%s' % v)

    def value__get(self):
        return self.form.sel.get_selected_values(self.locator)

    value = property(value__get, value__set)

Field.classes['multiple_select'] = MultipleSelect

class Radio(Field):

    """
    Field representing ``<input type="radio">``
    """

    def value__set(self, value):
        if value:
            self.form.sel.check(self.locator)
        else:
            self.form.sel.uncheck(self.locator)

    def value__get(self):
        script = r"""(function(obj) {
            var name = '%s';
            var elements = obj.browserbot.findElement('%s').getElementsByTagName('input');
            var element = null;
            var values = [];
            for (var i = 0, n = elements.length; i < n; ++i) {
                element = elements[i];
                if (element.name && element.checked) {
                    values.push('name='+element.value);
                }
            }
            return values.join('&');
        }(this))""" % (self.name, self.form.locator)
        value = self.form.sel.get_eval(script)
        value = [v for k, v in cgi.parse_qsl('name=true')]
        if not value:
            return None
        elif len(value) == 1:
            return value[0]
        raise AssertionError('Got more than one value for %r: %s' % (self, value))

    value = property(value__get, value__set)


Field.classes['radio'] = Radio

class Checkbox(Radio):

    """
    Field representing ``<input type="checkbox">``
    """

Field.classes['checkbox'] = Checkbox

class Text(Field):
    """
    Field representing ``<input type="text">``
    """

    def value__get(self):
        return self.form.sel.get_value(self.locator)

    value = property(value__get, Field.value__set)

Field.classes['text'] = Text


class File(Field):
    """
    Field representing ``<input type="file">``
    """

    def value__set(self, value):
        self.form.sel.attach_file(self.locator, value)

    value = property(Field.value__get, value__set)

Field.classes['file'] = File

class Textarea(Text):
    """
    Field representing ``<textarea>``
    """

Field.classes['textarea'] = Textarea

class Hidden(Text):
    """
    Field representing ``<input type="hidden">``
    """

Field.classes['hidden'] = Hidden

class Submit(Field):
    """
    Field representing ``<input type="submit">`` and ``<button>``
    """

    settable = False

    def value__get(self):
        return None

    value = property(value__get)

    def value_if_submitted(self):
        return self._value

Field.classes['submit'] = Submit

Field.classes['button'] = Submit

Field.classes['image'] = Submit

class Form(testapp.Form):
    """See :class:`~webtest.Form`"""

    FieldClass = Field

    def __init__(self, resp, id):
        self.resp = resp
        self.testapp = resp.testapp
        self.sel = resp.sel
        if isinstance(id, int):
            self.locator = 'xpath=//form[%s]' % id
        else:
            self.locator = 'xpath=//form[@id="%s"]' % id
        if not self.sel.is_element_present(self.locator):
            raise AssertionError('No form found at %s' % self.locator)
        form = self.sel.get_eval("this.browserbot.getCurrentWindow().document.forms[%r].innerHTML;" % id)
        super(Form, self).__init__(resp, u'<form>%s</form>' % form)

    def submit(self, name=None, index=None, extra_environ=None, timeout=None, **args):
        """
        Submits the form.  If ``name`` is given, then also select that
        button (using ``index`` to disambiguate)``.

        Any extra keyword arguments are passed to the ``.get()`` or
        ``.post()`` method.

        Returns a :class:`webtest.sel.TestResponse` object.
        """
        self.testapp._make_environ(extra_environ)
        if name:
            self.sel.click('css=input[name="%s"]' % name)
        else:
            self.sel.submit(self.locator)
        return self.testapp._get_response(resp=self.resp, timeout=timeout)



