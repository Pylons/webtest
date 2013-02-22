# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from tests.compat import unittest

import webtest

from webob import Request, Response

from webtest.lint import check_headers
from webtest.lint import check_content_type

from six import PY3


def application(environ, start_response):
    req = Request(environ)
    resp = Response()
    env_input = environ['wsgi.input']
    len_body = len(req.body)
    env_input.input.seek(0)
    if req.path_info == '/read':
        resp.body = env_input.read(len_body)
    elif req.path_info == '/read_line':
        resp.body = env_input.readline(len_body)
    elif req.path_info == '/read_lines':
        resp.body = b'-'.join(env_input.readlines(len_body))

    return resp(environ, start_response)


class TestCheckContentType(unittest.TestCase):
    def test_no_content(self):
        status = "204 No Content"
        headers = [
            ('Content-Type', 'text/plain; charset=utf-8'),
            ('Content-Length', '4')
        ]
        self.assertRaises(AssertionError, check_content_type, status, headers)

    def test_no_content_type(self):
        status = "200 OK"
        headers = [
            ('Content-Length', '4')
        ]
        self.assertRaises(AssertionError, check_content_type, status, headers)


class TestInputWrapper(unittest.TestCase):
    def test_read(self):
        app = webtest.TestApp(application)
        resp = app.post('/read', 'hello')
        self.assertEqual(resp.body, b'hello')

    def test_readline(self):
        app = webtest.TestApp(application)
        resp = app.post('/read_line', 'hello\n')
        self.assertEqual(resp.body, b'hello\n')

    def test_readlines(self):
        app = webtest.TestApp(application)
        resp = app.post('/read_lines', 'hello\nt\n')
        self.assertEqual(resp.body, b'hello\n-t\n')


class TestCheckHeaders(unittest.TestCase):

    @unittest.skipIf(not PY3, 'Useless in Python2')
    def test_header_unicode_value(self):
        self.assertRaises(AssertionError, check_headers, [('X-Price', '100€')])

    @unittest.skipIf(not PY3, 'Useless in Python2')
    def test_header_unicode_name(self):
        self.assertRaises(AssertionError, check_headers, [('X-€', 'foo')])
