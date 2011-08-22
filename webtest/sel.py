# (c) 2005 Ian Bicking and contributors; written for Paste
# (http://pythonpaste.org)
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php
"""
Routines for testing WSGI applications with selenium.

Most interesting is :class:`~webtest.sel.SeleniumApp` and the
:func:`~webtest.sel.with_selenium` decorator
"""
import os
import cgi
import sys
import time
import urllib
import signal
import socket
import webob
import signal
import httplib
import warnings
import threading
import subprocess
from functools import wraps
from webtest import app as testapp
from wsgiref import simple_server

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except:
        json = False


def is_selenium_available():
    """return True if the selenium module is available and a RC server is
    running"""
    if json == False:
        warnings.warn(
            ('selenium is not available because no json module are '
            'available. Consider installing simplejson'),
            SeleniumWarning)
    host = os.environ.get('SELENIUM_HOST', '127.0.0.1')
    port = int(os.environ.get('SELENIUM_POST', 4444))
    try:
        conn = httplib.HTTPConnection(host, port)
        conn.request('GET', '/')
    except socket.error:
        if 'SELENIUM_JAR' not in os.environ:
            return False
        else:
            jar = os.environ['SELENIUM_JAR']
            if os.path.isfile(jar):
                p = subprocess.Popen(['java', '-jar', jar])
                os.environ['SELENIUM_PID'] = str(p.pid)
                for i in range(30):
                    time.sleep(.3)
                    try:
                        conn = httplib.HTTPConnection(host, port)
                        conn.request('GET', '/')
                    except socket.error:
                        pass
                    else:
                        return True
            return False
    return True


def with_selenium(commands=()):
    """A decorator to run tests only when selenium is available"""
    if 'SELENIUM_COMMAND' in os.environ:
        command = os.environ['SELENIUM_COMMAND'].strip('*')
        commands = ('*%s' % command,)
    elif not commands:
        commands = ('*googlechrome',)

    def wrapped(func_or_class):
        if is_selenium_available():
            if isinstance(func_or_class, type):
                return func_or_class
            else:
                @wraps(func_or_class)
                def wrapper(self):
                        old_app = self.app
                        for command in commands:
                            self.app = SeleniumApp(self.app.app,
                                                   command=command)
                            try:
                                res = func_or_class(self)
                            finally:
                                self.app.close()
                                self.app = old_app
                return wrapper
    return wrapped


class SeleniumWarning(Warning):
    """Specific warning category"""


class WSGIApplication(object):
    """A WSGI middleware to handle special calls used to run a test app"""

    def __init__(self, app, port):
        self.app = app
        self.serve_forever = True
        self.port = port
        self.url = 'http://localhost:%s/' % port
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

class Selenium(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.session_id = None

    def start(self, command, url):
        self.session_id = self.execute('getNewBrowserSession',
                                       command, url,
                                       "captureNetworkTraffic=true",
                                       "addCustomRequestHeader=true")

    def stop(self):
        self.execute("testComplete")
        self.session_id = None

    def execute(self, cmd, *args):
        data = dict([(i+1, a) for i, a in enumerate(args)], cmd=cmd)
        if self.session_id:
            data['sessionId'] = self.session_id
        data = urllib.urlencode(data)
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
          }
        conn = httplib.HTTPConnection(self.host, self.port)
        try:
            conn.request("POST", "/selenium-server/driver/", data, headers)
            resp = conn.getresponse()
            status = resp.status
            data = resp.read()
        finally:
            conn.close()
        if data.startswith('ERROR: Unknown command:'):
            raise AttributeError(repr(data))
        elif not data.startswith('OK'):
            raise RuntimeError(repr(data))
        data = data[3:]
        if data in ('true', 'false'):
            return data == 'true' and True or False
        return data

class SeleniumApp(testapp.TestApp):
    """See :class:`webtest.TestApp`

    SeleniumApp only support ``GET`` requests
    """

    apps = []

    def __init__(self, app=None, url=None,
                 command='*chrome', timeout=4000,
                 extra_environ=None, relative_to=None, **kwargs):
        self.app = None
        if app:
            super(SeleniumApp, self).__init__(app, relative_to=relative_to)
            self._run_server(self.app)
            url = self.app.url
        assert is_selenium_available()
        self.session_id = None
        host = os.environ.get('SELENIUM_HOST', '127.0.0.1')
        port = int(os.environ.get('SELENIUM_POST', 4444))
        if 'SELENIUM_COMMAND' in os.environ:
            command = os.environ['SELENIUM_COMMAND'].strip('*')
            command = '*%s' % command
        self.sel = Selenium(host, port)
        self.sel.start(command, url)
        self.extra_environ = extra_environ or {}
        self.timeout = timeout
        self.test_app = self
        self.firefox = self.chrome = self.ie = None
        if command == '*chrome':
            self.firefox = True
        elif command == '*googlechrome':
            self.chrome = True
        elif command == '*iexplore':
            self.ie = True

    def do_request(self, req, status, expect_errors):
        if req.method != 'GET':
            raise testapp.AppError('Only GET are allowed')
        if self.app:
            req.host = 'localhost:%s' % self.app.port
        self.sel.execute('captureNetworkTraffic', 'json')
        for h, v in req.headers.items():
            self.sel.execute('addCustomRequestHeader', h, v)
        self.sel.execute('open', req.url)
        resp = self._get_response()
        if not expect_errors:
            self._check_status(status, resp)
            if not status:
                status = resp.status_int
                if not (status > 300 and status < 400):
                    self._check_errors(resp)
        return resp


    def _get_response(self, resp=None, timeout=None):
        """Get responses responses from selenium"""
        if timeout != 0:
            timeout = timeout or self.timeout
            self.sel.execute('waitForPageToLoad', timeout)
        trafic = json.loads(self.sel.execute('captureNetworkTraffic', 'json'))
        responses = []
        errors = []
        for d in trafic:
            if d['url'].endswith('.ico'):
                continue
            req = webob.Request.blank(d['url'])
            for h in d['requestHeaders']:
                req.headers[h['name']] = h['value']
            resp = TestResponse()
            resp.app = self.test_app
            resp.sel = self.test_app.sel
            resp.responses = responses
            resp.errors = errors
            resp.request = req
            resp.status = str(d['statusCode'])
            for h in d['responseHeaders']:
                resp.headers[h['name']] = h['value']
            if resp.status_int == 200 and 'text/' in resp.content_type:
                if not resp.charset:
                    resp.charset = 'utf-8'
            if resp.status_int > 400:
                errors.append('%s %r' % (resp.request.url, resp))
            if 'html' in resp.content_type or resp.status_int != 200:
                responses.append(resp)
        if responses:
            resp = responses.pop(0)
            print resp.errors
            return resp
        elif resp is not None:
            return resp
        else:
            raise LookupError('No response found')

    def _run_server(self, app):
        """Run a wsgi server in a separate thread"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        time.sleep(.3)
        while True:
            try:
                conn.request('GET', '/__application__')
                resp = conn.getresponse()
            except (socket.error, httplib.CannotSendRequest), e:
                time.sleep(.1)
            else:
                break

    def close(self):
        """Close selenium and the WSGI server if needed"""
        if self.app:
            conn = httplib.HTTPConnection("127.0.0.1", self.app.port)
            while True:
                try:
                    conn.request('GET', '/__kill_application__')
                    resp = conn.getresponse()
                except socket.error:
                    self.app.thread.join()
                    break
        if 'SELENIUM_KEEP_OPEN' not in os.environ:
            self.sel.execute("testComplete")
            self.sessionId = None
        if 'SELENIUM_PID' in os.environ:
            os.kill(int(os.environ['SELENIUM_PID']), signal.SIGKILL)


class Element(object):
    """A object use to manipulate DOM nodes. This object allow to use the
    underlying selenium api for the specified locator. See Selenium `api <http://goo.gl/IecEk>`_
    """

    def __init__(self, resp, locator):
        self.sel = resp.sel
        self.resp = resp
        self.locator = locator

    def __getattr__(self, attr):
        meth = getattr(self.sel, attr, None)
        if meth is not None:
            def wrapped(*args):
                args = [self.locator] + [str(a) for a in args]
                return meth(*args)
        else:
            def wrapped(*args):
                args = [attr, self.locator] + [str(a) for a in args]
                return self.sel.execute(*args)
        if meth:
            wraps(meth)(wrapped)
        else:
            wrapped.__name__ = attr
        return wrapped

    def wait(self, timeout=3000):
        """Wait for an element and return this element"""
        ctime = time.time() + (timeout / 1000)
        while ctime >= time.time():
            if self.isElementPresent():
                return self
        raise RuntimeError("Can't find %s after %sms" % (self, timeout))

    def hasClass(self, name):
        """True iif the class is present"""
        classes = self.eval('e.getAttribute("class")').split()
        return name in classes

    def html(self):
        """Return the innerHTML of the element"""
        return self.eval('e.innerHTML')

    @property
    def value(self):
        """Return value (only work with text field)"""
        return self.getValue()

    def eval(self, expr):
        """Eval a javascript expression in Selenium RC. You can use the
        following variables:

        - s: the ``selenium`` object
        - b: the ``browserbot`` object
        - e: the element itself
        """
        script = r'''(function(s) {
            var b = s.browserbot;
            var e = b.findElement("%s");
            var res = %s;
            return res || 'null';
        }(this))''' % (self.locator.replace('"', "'"), expr.strip(';'))
        return self.sel.execute('getEval', script)

    def __contains__(self, s):
        if isinstance(s, self.__class__):
            s = s.html()
        return s in self.html()

    def __repr__(self):
        return '<%s at %s>' % (self.__class__.__name__, self.locator)

    def __str__(self):
        return self.locator

class Document(object):
    """The browser document. ``resp.doc.myid`` is egual to
    ``resp.doc.css('#myid')``"""

    def __init__(self, resp):
        self.resp = resp

    def __getattr__(self, attr):
        return Element(self.resp, 'css=#%s' % attr)

    def get(self, tag, **kwargs):
        """Return an element matching ``tag``, an ``attribute`` and an
        ``index``.  For example::

            resp.doc.get('input', name='myinput') => xpath=//input[@name="myinput"]
            resp.doc.get('li', description='Item') => xpath=//li[.="Item"]
        """
        locator = _eval_xpath(tag, **kwargs)
        return Element(self.resp, locator)

    def xpath(self, path):
        """Get an :class:`~webtest.sel.Element` using xpath"""
        return Element(self.resp, 'xpath=%s' % path)

    def css(self, selector):
        """Get an :class:`~webtest.sel.Element` using a css selector"""
        return Element(self.resp, 'css=%s' % selector)

    def link(self, description=None, linkid=None, href=None, index=None):
        """Get a link"""
        return self.get('a', description=description, id=linkid,
                             href=href, index=index)

    def input(self, value=None, name=None, inputid=None, index=None):
        """Get an input field"""
        return self.get('input', id=inputid,
                                 value=value, name=name, index=index)

    def button(self, description=None, buttonid=None, index=None):
        """Get a button"""
        return self.get('button', description=description,
                                 id=buttonid, index=index)


class TestResponse(testapp.TestResponse):

    def follow(self, status=None, **kw):
        """If this request is a redirect, follow that redirect.  It
        is an error if this is not a redirect response.  Returns
        another response object.
        """
        if not (self.status_int >= 300 and self.status_int < 400):
            raise ValueError(
               'You can only follow 301 and 302. Not %s' % self.status_int)
        if len(self.responses):
            resp = self.responses[0]
            if not kw.get('expect_errors', False):
                self.app._check_status(status, resp)
                if not status:
                    self.app._check_errors(resp)
            return self.responses.pop(0)
        raise LookupError('Responses queue is empty. Nothing to follow.')

    def click(self, description=None, linkid=None, href=None,
              anchor=None, index=None, verbose=False,
              extra_environ=None, timeout=None):
        link = self.doc.link(description=description, linkid=linkid,
                             href=href, index=index)
        link.click()
        if timeout == 0:
            return self
        return self.test_app._get_response(resp=self, timeout=timeout)

    @property
    def forms(self):
        return Forms(self)

    @property
    def form(self):
        return Form(self, 0)

    def _body__get(self):
        body = self.sel.execute('getHtmlSource')
        if isinstance(body, unicode):
            return body.encode(self.charset or 'utf-8')
        else:
            return body

    body = property(_body__get)

    def __contains__(self, item):
        if isinstance(item, Element):
            return item.isElementPresent()
        return super(TestResponse, self).__contains__(item)

    @property
    def doc(self):
        """Expose a :class:`~webtest.sel.Document`"""
        return Document(self)


class Field(testapp.Field, Element):

    classes = {}

    def __init__(self, *args, **kwargs):
        super(Field, self).__init__(*args, **kwargs)
        self.sel = self.form.sel
        self.options = []
        self.selectedIndices = []
        self._forced_values = []
        self.locator = _eval_xpath(self.tag,
                                   locator=self.form.locator,
                                    name=self.name)

    def value__set(self, value):
        if not self.settable:
            raise AttributeError(
                "You cannot set the value of the <%s> field %r"
                % (self.tag, self.name))
        self.type(value)

    def value__get(self):
        return self.getValue()

    value = property(value__get, value__set)


class Select(Field):
    """Field representing ``<select>``"""

    def force_value(self, value):
        self.select('value=%s' % value)

    def value__set(self, value):
        self.select('value=%s' % value)

    def value__get(self):
        return self.getSelectedValue()

    value = property(value__get, value__set)

Field.classes['select'] = Select


class MultipleSelect(Field):
    """Field representing ``<select multiple="multiple">``"""

    def force_value(self, values):
        self.removeAllSelections()
        str_values = [testapp._stringify(value) for value in values]
        for v in str_values:
            self.addSelection('value=%s' % v)

    def value__set(self, values):
        self.removeAllSelections()
        str_values = [testapp._stringify(value) for value in values]
        for v in str_values:
            self.addSelection('value=%s' % v)

    def value__get(self):
        value = self.getSelectedValues()
        return value.split(',')

    value = property(value__get, value__set)

Field.classes['multiple_select'] = MultipleSelect


class Radio(Field):
    """Field representing ``<input type="radio">``"""

    def value__set(self, value):
        if value:
            self.check()
        else:
            self.uncheck()

    def value__get(self):
        script = r"""(function(obj) {
            var name = '%s';
            var element = obj.browserbot.findElement('%s');
            var elements = element.getElementsByTagName('input');
            var values = [];
            for (var i = 0, n = elements.length; i < n; ++i) {
                element = elements[i];
                if (element.name == name && element.checked) {
                    values.push('name='+element.value);
                }
            }
            return values.join('&');
        }(this))""" % (self.name, self.form.locator)
        value = self.sel.execute('getEval', script)
        value = [v for k, v in cgi.parse_qsl('name=true')]
        if not value:
            return None
        elif len(value) == 1:
            return value[0]
        raise ValueError(
                'Got more than one value for %r: %s' % (self, value))

    value = property(value__get, value__set)


Field.classes['radio'] = Radio


class Checkbox(Radio):
    """Field representing ``<input type="checkbox">``"""

Field.classes['checkbox'] = Checkbox


class Text(Field):
    """Field representing ``<input type="text">``"""

Field.classes['text'] = Text


class File(Field):
    """Field representing ``<input type="file">``"""

    def value__set(self, value):
        self.sel.attachFile(value)

    value = property(Field.value__get, value__set)

Field.classes['file'] = File


class Textarea(Text):
    """Field representing ``<textarea>``"""

Field.classes['textarea'] = Textarea


class Hidden(Text, testapp.Hidden):
    """Field representing ``<input type="hidden">``"""

Field.classes['hidden'] = Hidden


class Submit(Field, testapp.Submit):
    """Field representing ``<input type="submit">`` and ``<button>``"""

    settable = False

    def value__get(self):
        return None

    value = property(value__get)

    def value_if_submitted(self):
        return self._value

Field.classes['submit'] = Submit

Field.classes['button'] = Submit

Field.classes['image'] = Submit


class Forms(object):

    def __init__(self, resp):
        self.resp = resp

    def __getitem__(self, key):
        return Form(self.resp, key)


class Form(testapp.Form):
    """See :class:`~webtest.Form`"""

    FieldClass = Field

    def __init__(self, resp, id):
        self.resp = resp
        self.test_app = resp.test_app
        self.sel = resp.sel
        if isinstance(id, int):
            self.locator = _eval_xpath('form', index=id)
        else:
            self.locator = _eval_xpath('form', id=id)
        if not self.sel.execute('isElementPresent', self.locator):
            raise LookupError('No form found at %s' % self.locator)
        form = self.sel.execute('getEval',
            "this.browserbot.findElement('%s').innerHTML;" % self.locator)
        super(Form, self).__init__(resp, u'<form>%s</form>' % form)

    def _parse_fields(self):
        super(Form, self)._parse_fields()
        # Add index to locators
        for name, fields in self.fields.items():
            if len(fields) > 1:
                for i, field in enumerate(fields):
                    field.locator += '[%s]' % (i + 1,)


    def submit(self, name=None, index=None, extra_environ=None, timeout=None):
        """Submits the form.  If ``name`` is given, then also select that
        button (using ``index`` to disambiguate)``.

        Any extra keyword arguments are passed to the ``.get()`` or
        ``.post()`` method.

        Returns a :class:`webtest.sel.TestResponse` object.
        """
        if timeout != 0:
            self.sel.execute('captureNetworkTraffic', 'json')
        self.test_app._make_environ(extra_environ)
        if name:
            selector = _eval_xpath('input', locator=self.locator,
                                    name=name, index=index)
            self.sel.execute('click', selector)
        else:
            self.sel.execute('submit', self.locator)
        return self.test_app._get_response(resp=self.resp, timeout=timeout)


def _eval_xpath(tag, locator=None, index=None, **kwargs):
    if not locator:
        locator = 'xpath='
    locator += "//%s" % tag
    for k, v in kwargs.items():
        if k in ('for_', 'class_'):
            k = k.strip('_')
        if v:
            if k == 'description':
                locator += '[.="%s"]' % v
            else:
                locator += '[@%s="%s"]' % (k, v)
    if index is not None:
        locator += '[%s]' % (index + 1,)
    return locator
