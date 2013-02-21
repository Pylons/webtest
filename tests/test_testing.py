# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import sys
import six
import webtest
from webtest.debugapp import debug_app
from webtest.compat import PY3
from webtest.compat import to_bytes
from webtest.compat import print_stderr
from webtest.app import AppError
from tests.compat import unittest
import webbrowser


def test_print_unicode():
    print_stderr('°C')


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

    def test_post_unicode(self):
        res = self.app.post('/', params=dict(a='é'),
               content_type='application/x-www-form-urlencoded;charset=utf8')
        res.mustcontain('a=%C3%A9')

    def test_post_unicode_body(self):
        res = self.app.post('/', params='é',
               content_type='text/plain; charset=utf8')
        self.assertTrue(res.body.endswith(b'\xc3\xa9'))
        res.mustcontain('é')

    def test_post_params(self):
        res = self.app.post('/', params=dict(a=1))
        res.mustcontain('a=1')
        res = self.app.post('/', params=[('a', '1')])
        res.mustcontain('a=1')
        res = self.app.post_json('/', params=dict(a=1))
        res.mustcontain('{"a": 1}')
        res = self.app.post_json('/', params=False)
        res.mustcontain('false')

    def test_put_params(self):
        res = self.app.put('/', params=dict(a=1))
        res.mustcontain('a=1')
        res = self.app.put_json('/', params=dict(a=1))
        res.mustcontain('{"a": 1}')
        res = self.app.put_json('/', params=False)
        res.mustcontain('false')

    def test_delete_params(self):
        res = self.app.delete('/', params=dict(a=1))
        res.mustcontain('a=1')
        res = self.app.delete_json('/', params=dict(a=1))
        res.mustcontain('{"a": 1}')

    def test_options(self):
        res = self.app.options('/')
        self.assertEqual(res.status_int, 200)

    def test_exception(self):
        self.assertRaises(Exception, self.app.get, '/?error=t')
        self.assertRaises(webtest.AppError, self.app.get,
                                            '/?status=404%20Not%20Found')

    def test_bad_content_type(self):
        resp = self.app.get('/')
        self.assertRaises(AttributeError, lambda: resp.json)
        resp = self.app.get('/?header-content-type=application/json')
        self.assertRaises(AttributeError, lambda: resp.pyquery)
        self.assertRaises(AttributeError, lambda: resp.lxml)
        self.assertRaises(AttributeError, lambda: resp.xml)

    def test_app_from_config_file(self):
        config = os.path.join(os.path.dirname(__file__), 'deploy.ini')
        app = webtest.TestApp('config:%s#main' % config)
        resp = app.get('/')
        self.assertEqual(resp.status_int, 200)


    def test_errors(self):
        try:
            self.app.get('/?errorlog=somelogs')
            assert(False, "An AppError should be raised")
        except AppError:
            e = sys.exc_info()[1]
            assert six.text_type(e) \
                == "Application had errors logged:\nsomelogs"

    def test_request_obj(self):
        res = self.app.get('/')
        res = self.app.request(res.request)

    def test_showbrowser(self):
        open_new = webbrowser.open_new
        self.filename = ''

        def open_new(f):
            self.filename = f

        webbrowser.open_new = open_new
        res = self.app.get('/')
        res.showbrowser()
        assert self.filename.startswith('file://'), self.filename

    def test_303(self):
        res = self.app.get('/?status=302%20Redirect&header-location=/foo')
        self.assertEqual(res.status_int, 302)
        print(res.location)
        self.assertEqual(res.location, 'http://localhost/foo', res)
        self.assertEqual(res.headers['location'], 'http://localhost/foo')
        res = res.follow()
        self.assertEqual(res.request.url, 'http://localhost/foo')
        self.assertIn('Response: 200 OK', str(res))
        self.assertIn('200 OK', repr(res))
        self.app.get('/?status=303%20redirect', status='3*')

    def test_204(self):
        self.app.post('/?status=204%20OK')

    def test_404(self):
        self.app.get('/?status=404%20Not%20Found', status=404)
        self.assertRaises(webtest.AppError, self.app.get, '/', status=404)

    def test_print_stderr(self):
        res = self.app.get('/')
        res.charset = 'utf-8'
        res.text = '°C'
        print_stderr(str(res))

        res.charset = None
        print_stderr(str(res))

    def test_app_error(self):
        res = self.app.get('/')
        res.charset = 'utf-8'
        res.text = '°C'
        AppError('%s %s %s %s', res.status, '', res.request.url, res)
        res.charset = None
        AppError('%s %s %s %s', res.status, '', res.request.url, res)

    def test_exception_repr(self):
        res = self.app.get('/')
        res.charset = 'utf-8'
        res.text = '°C'
        if not PY3:
            unicode(AssertionError(res))
        str(AssertionError(res))
        res.charset = None
        if not PY3:
            unicode(AssertionError(res))
        str(AssertionError(res))

    def test_fake_dict(self):
        class FakeDict(object):
            def items(self):
                return [('a', '10'), ('a', '20')]
        self.app.post('/params', params=FakeDict())
