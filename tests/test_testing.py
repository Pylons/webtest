# -*- coding: utf-8 -*-
import webtest
from webtest.debugapp import debug_app
from webtest.compat import to_bytes
from webtest.compat import print_stderr
from tests.compat import unittest
from tests.compat import u


def test_print_unicode():
    print_stderr(u('°C'))


class TestTesting(unittest.TestCase):

    def setUp(self):
        self.app = webtest.TestApp(debug_app)

    def test_url_class(self):
        class U:
            def __str__(self):
                return '/'
        res = self.app.get(U())
        self.assertEqual(res.status_int, 200)

    def test_testing(self):
        res = self.app.get('/')
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.headers['content-type'], 'text/plain')
        self.assertEqual(res.content_type, 'text/plain')
        res = self.app.request('/', method='GET')
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.headers['content-type'], 'text/plain')
        self.assertEqual(res.content_type, 'text/plain')
        res = self.app.head('/')
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.headers['content-type'], 'text/plain')
        self.assertTrue(res.content_length > 0)
        self.assertEqual(res.body, to_bytes(''))

    def test_get_params(self):
        res = self.app.post('/', params=dict(a=1))
        res.mustcontain('a=1')
        res = self.app.post('/', params=[('a','1')])
        res.mustcontain('a=1')

    def test_delete_params(self):
        res = self.app.delete('/', params=dict(a=1))
        res.mustcontain('a=1')

    def test_options(self):
        res = self.app.options('/')
        self.assertEqual(res.status_int, 200)

    def test_exception(self):
        self.assertRaises(Exception, self.app.get, '/?error=t')
        self.assertRaises(webtest.AppError, self.app.get, '/?status=404%20Not%20Found')

    def test_303(self):
        res = self.app.get('/?status=303%20Redirect&header-location=/foo')
        self.assertEqual(res.status_int, 303)
        print(res.location)
        self.assertEqual(res.location, '/foo')
        self.assertEqual(res.headers['location'], '/foo')
        res = res.follow()
        self.assertEqual(res.request.url, 'http://localhost/foo')
        self.assertIn('Response: 200 OK', str(res))
        self.assertIn('200 OK', repr(res))
        res = self.app.get('/?status=303%20redirect', status='3*')

    def test_204(self):
        res = self.app.post('/?status=204%20OK')

    def test_404(self):
        self.app.get('/?status=404%20Not%20Found', status=404)
        self.assertRaises(webtest.AppError, self.app.get, '/', status=404)

    def test_fake_dict(self):
        class FakeDict(object):
            def items(self):
                return [('a', '10'), ('a', '20')]
        res = self.app.post('/params', params=FakeDict())

