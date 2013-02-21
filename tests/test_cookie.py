import datetime

from webob import Request
import mock

from webtest.compat import to_bytes
from tests.compat import unittest
import webtest


def cookie_app(environ, start_response):
    req = Request(environ)
    status = "200 OK"
    body = '<html><body><a href="/go/">go</a></body></html>'
    headers = [
        ('Content-Type', 'text/html'),
        ('Content-Length', str(len(body))),
    ]
    if req.path_info != '/go/':
        headers.extend([
            ('Set-Cookie', 'spam=eggs'),
            ('Set-Cookie', 'foo=bar;baz'),
        ])
    start_response(status, headers)
    return [to_bytes(body)]


def cookie_app3(environ, start_response):
    status = to_bytes("200 OK")
    body = 'Cookie: %(HTTP_COOKIE)s' % environ
    headers = [
        ('Content-Type', 'text/html'),
        ('Content-Length', str(len(body))),
    ]
    start_response(status, headers)
    return [to_bytes(body)]


def cookie_app4(environ, start_response):
    status = to_bytes("200 OK")
    body = ''
    headers = [
        ('Content-Type', 'text/html'),
        ('Content-Length', str(len(body))),
        ('Set-Cookie', 'spam=eggs; Expires=Tue, 21-Feb-2013 17:45:00 GMT;'),
    ]
    start_response(status, headers)
    return [to_bytes(body)]


class TestCookies(unittest.TestCase):

    def test_response_set_cookie(self):
        app = webtest.TestApp(cookie_app)
        self.assertTrue(not app.cookiejar,
                        'App should initially contain no cookies')
        app.get('/')
        cookies = app.cookies
        self.assert_(cookies, 'Response should have set cookies')
        self.assertEqual(cookies['spam'].value, 'eggs')
        self.assertEqual(cookies['foo'].value, 'bar')

    def test_preserves_cookies(self):
        app = webtest.TestApp(cookie_app)
        res = app.get('/')
        self.assert_(app.cookiejar)
        res.click('go')
        self.assert_(app.cookiejar)

    def test_send_cookies(self):
        app = webtest.TestApp(cookie_app3)
        self.assertTrue(not app.cookies,
                        'App should initially contain no cookies')

        resp = app.get('/', headers=[('Cookie', 'spam=eggs')])
        self.assertFalse(app.cookies,
                         'Response should not have set cookies')
        resp.mustcontain('Cookie: spam=eggs')

    @mock.patch('six.moves.http_cookiejar.time.time')
    def test_expires_cookies(self, mock_time):
        app = webtest.TestApp(cookie_app4)
        self.assertTrue(not app.cookiejar,
                        'App should initially contain no cookies')

        mock_time.return_value = 1361464946.0
        app.get('/')
        self.assertTrue(app.cookies, 'Response should have set cookies')

        mock_time.return_value = 1461464946.0
        app.get('/')
        self.assertFalse(app.cookies, 'Response should have unset cookies')

    def test_cookies_readonly(self):
        app = webtest.TestApp(cookie_app)
        try:
            app.cookies = {}
        except:
            pass
        else:
            self.fail('testapp.cookies should be read-only')
