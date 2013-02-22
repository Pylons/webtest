# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from tests.compat import unittest

import webtest

from webob import Request, Response

from webtest.lint import check_headers
from webtest.lint import check_content_type
from webtest.lint import check_environ
from webtest.lint import IteratorWrapper
from webtest.lint import WriteWrapper
from webtest.lint import ErrorWrapper
from webtest.lint import InputWrapper

from webtest.compat import to_bytes

from six import PY3
from six import StringIO

import warnings


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
        input_wrapper = InputWrapper(None)
        self.assertRaises(AssertionError,input_wrapper.close)


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


class TestCheckHeaders(unittest.TestCase):

    @unittest.skipIf(not PY3, 'Useless in Python2')
    def test_header_unicode_value(self):
        self.assertRaises(AssertionError, check_headers, [('X-Price', '100€')])

    @unittest.skipIf(not PY3, 'Useless in Python2')
    def test_header_unicode_name(self):
        self.assertRaises(AssertionError, check_headers, [('X-€', 'foo')])


class TestCheckEnviron(unittest.TestCase):
    def test_no_query_string(self):
        environ = {
            'REQUEST_METHOD': str('GET'),
            'SERVER_NAME': str('localhost'),
            'SERVER_PORT': str('80'),
            'wsgi.version': (1, 0, 1),
            'wsgi.input': StringIO('test'),
            'wsgi.errors': StringIO(),
            'wsgi.multithread': None,
            'wsgi.multiprocess': None,
            'wsgi.run_once': None,
            'wsgi.url_scheme': 'http',
            'PATH_INFO': str('/'),
        }
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            check_environ(environ)
            self.assertEqual( len(w), 1, "We should have only one warning")
            self.assertTrue( "QUERY_STRING" in str(w[-1].message), 
                "The warning message should say something about QUERY_STRING")

    def test_no_valid_request(self):
        environ = {
            'REQUEST_METHOD': str('PROPFIND'),
            'SERVER_NAME': str('localhost'),
            'SERVER_PORT': str('80'),
            'wsgi.version': (1, 0, 1),
            'wsgi.input': StringIO('test'),
            'wsgi.errors': StringIO(),
            'wsgi.multithread': None,
            'wsgi.multiprocess': None,
            'wsgi.run_once': None,
            'wsgi.url_scheme': 'http',
            'PATH_INFO': str('/'),
            'QUERY_STRING': str(''),
        }
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            check_environ(environ)
            self.assertEqual( len(w), 1, "We should have only one warning")
            self.assertTrue( "REQUEST_METHOD" in str(w[-1].message),
                'The warning message should say something about REQUEST_METHOD')


class TestIteratorWrapper(unittest.TestCase):
    def test_close(self):
        class MockIterator(object):

            def __init__(self):
                self.closed = False

            def __iter__(self):
                return self

            def __next__(self):
                return None

            next = __next__

            def close(self):
                self.closed = True

        mock = MockIterator()
        wrapper = IteratorWrapper(mock, None)
        wrapper.close()

        self.assertTrue(mock.closed, "Original iterator has not been closed")


class TestWriteWrapper(unittest.TestCase):
    def test_wrong_type(self):
        write_wrapper = WriteWrapper(None)
        self.assertRaises(AssertionError, write_wrapper, 'not a binary')

    def test_normal(self):
        class MockWriter(object):
            def __init__(self):
                self.written = []

            def __call__(self, s):
                self.written.append(s)

        data = to_bytes('foo')
        mock = MockWriter()
        write_wrapper = WriteWrapper(mock)
        write_wrapper(data)
        self.assertEqual(mock.written, [data], 
            "WriterWrapper should call original writer when data is binary "
            "type")


class TestErrorWrapper(unittest.TestCase):

    def test_dont_close(self):
        error_wrapper = ErrorWrapper(None)
        self.assertRaises(AssertionError, error_wrapper.close)

    class FakeError(object):
        def __init__(self):
            self.written = []
            self.flushed = False

        def write(self, s):
            self.written.append(s)

        def writelines(self, lines):
            for line in lines:
                self.write(line)

        def flush(self):
            self.flushed = True

    def test_writelines(self):
        fake_error = self.FakeError()
        error_wrapper = ErrorWrapper(fake_error)
        data = [to_bytes('a line'), to_bytes('another line')]
        error_wrapper.writelines(data)
        self.assertEqual(fake_error.written, data, 
            "ErrorWrapper should call original writer")

    def test_flush(self):
        fake_error = self.FakeError()
        error_wrapper = ErrorWrapper(fake_error)
        error_wrapper.flush()
        self.assertTrue(fake_error.flushed, 
            "ErrorWrapper should have called original wsgi_errors's flush")
