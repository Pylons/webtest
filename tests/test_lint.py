# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from six import PY3
from six import StringIO
from tests.compat import unittest
from webob import Request, Response

import warnings
import mock

from webtest import TestApp
from webtest.compat import to_bytes
from webtest.lint import check_headers
from webtest.lint import check_content_type
from webtest.lint import check_environ
from webtest.lint import IteratorWrapper
from webtest.lint import WriteWrapper
from webtest.lint import ErrorWrapper
from webtest.lint import InputWrapper
from webtest.lint import to_string
from webtest.lint import middleware

from six import BytesIO


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


class TestToString(unittest.TestCase):

    def test_to_string(self):
        self.assertEqual(to_string('foo'), 'foo')
        self.assertEqual(to_string(b'foo'), 'foo')


class TestMiddleware(unittest.TestCase):

    def test_lint_too_few_args(self):
        linter = middleware(application)
        with self.assertRaisesRegexp(AssertionError, "Two arguments required"):
            linter()
        with self.assertRaisesRegexp(AssertionError, "Two arguments required"):
            linter({})

    def test_lint_no_keyword_args(self):
        linter = middleware(application)
        with self.assertRaisesRegexp(AssertionError, "No keyword arguments "
                                                     "allowed"):
            linter({}, 'foo', baz='baz')

    #TODO: test start_response_wrapper

    @mock.patch.multiple('webtest.lint',
                         check_environ=lambda x: True,  # don't block too early
                         InputWrapper=lambda x: True)
    def test_lint_iterator_returned(self):
        linter = middleware(lambda x, y: None)  # None is not an iterator
        msg = "The application must return an iterator, if only an empty list"
        with self.assertRaisesRegexp(AssertionError, msg):
            linter({'wsgi.input': 'foo', 'wsgi.errors': 'foo'}, 'foo')


class TestInputWrapper(unittest.TestCase):
    def test_read(self):
        app = TestApp(application)
        resp = app.post('/read', 'hello')
        self.assertEqual(resp.body, b'hello')

    def test_readline(self):
        app = TestApp(application)
        resp = app.post('/read_line', 'hello\n')
        self.assertEqual(resp.body, b'hello\n')

    def test_readlines(self):
        app = TestApp(application)
        resp = app.post('/read_lines', 'hello\nt\n')
        self.assertEqual(resp.body, b'hello\n-t\n')

    def test_close(self):
        input_wrapper = InputWrapper(None)
        self.assertRaises(AssertionError, input_wrapper.close)

    def test_iter(self):
        data = to_bytes("A line\nAnother line\nA final line\n")
        input_wrapper = InputWrapper(BytesIO(data))
        self.assertEquals(to_bytes("").join(input_wrapper), data, '')

    def test_seek(self):
        data = to_bytes("A line\nAnother line\nA final line\n")
        input_wrapper = InputWrapper(BytesIO(data))
        input_wrapper.seek(0)
        self.assertEquals(to_bytes("").join(input_wrapper), data, '')


class TestMiddleware2(unittest.TestCase):
    def test_exc_info(self):
        def application_exc_info(environ, start_response):
            body = to_bytes('body stuff')
            headers = [
                ('Content-Type', 'text/plain; charset=utf-8'),
                ('Content-Length', str(len(body)))]
            start_response(to_bytes('200 OK'), headers, ('stuff',))
            return [body]

        app = TestApp(application_exc_info)
        app.get('/')
        # don't know what to assert here... a bit cheating, just covers code


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
            self.assertEqual(len(w), 1, "We should have only one warning")
            self.assertTrue(
                "QUERY_STRING" in str(w[-1].message),
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
            self.assertEqual(len(w), 1, "We should have only one warning")
            self.assertTrue(
                "REQUEST_METHOD" in str(w[-1].message),
                "The warning message should say something "
                "about REQUEST_METHOD")

    def test_handles_native_strings_in_variables(self):
        # "native string" means unicode in py3, but bytes in py2
        path = '/umläut'
        if not PY3:
            path = path.encode('utf-8')
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
            'PATH_INFO': path,
            'QUERY_STRING': str(''),
        }
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            check_environ(environ)
            self.assertEqual(0, len(w), "We should have no warning")


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
        self.assertEqual(
            mock.written, [data],
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
        self.assertTrue(
            fake_error.flushed,
            "ErrorWrapper should have called original wsgi_errors's flush")
