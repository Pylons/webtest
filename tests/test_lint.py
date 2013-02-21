# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from tests.compat import unittest

import webtest

from webob import Request, Response


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
    elif req.path_info == '/close':
        resp.body = env_input.close()
    return resp(environ, start_response)


def no_content_with_content(environ, start_response):
    status = "204 No Content"
    body = 'truc'
    headers = [
        ('Content-Type', 'text/plain; charset=utf-8'),
        ('Content-Length', str(len(body)))]
    start_response(status, headers)
    return [body]


def no_content_type(environ, start_response):
    status = "200 OK"
    body = 'truc'
    headers = [
        #('Content-Type', 'text/plain; charset=utf-8'),
        ('Content-Length', str(len(body)))]
    start_response(status, headers)
    return [body]


class TestForms(unittest.TestCase):
    def test_no_content(self):
        app = webtest.TestApp(no_content_with_content)
        self.assertRaises(AssertionError, app.get, '/')

    def test_no_content_type(self):
        app = webtest.TestApp(no_content_type)
        self.assertRaises(AssertionError, app.get, '/')


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

    def test_close(self):
        app = webtest.TestApp(application)
        self.assertRaises(AssertionError, app.post, 'close', 'hello')
