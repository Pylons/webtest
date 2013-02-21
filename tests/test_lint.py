# -*- coding: utf-8 -*-

from tests.compat import unittest

import webtest

from six import PY3

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
