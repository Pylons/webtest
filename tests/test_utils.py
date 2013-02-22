# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import re
import unittest

from json import dumps
from webtest import utils


class NoDefaultTest(unittest.TestCase):

    def test_nodefault(self):
        from webtest.utils import NoDefault
        self.assertEquals(repr(NoDefault), '<NoDefault>')


class encode_paramsTest(unittest.TestCase):

    def test_encode_params_None(self):
        self.assertEquals(utils.encode_params(None, None), None)

    def test_encode_params_NoDefault(self):
        self.assertEquals(utils.encode_params(utils.NoDefault, None), '')

    def test_encode_params_dict_or_list(self):
        self.assertEquals(utils.encode_params({'foo': 'bar'}, None),
                          utils.encode_params([('foo', 'bar')], None))

    def test_encode_params_no_charset(self):
        # no content_type at all
        self.assertEquals(utils.encode_params({'foo': 'bar'}, None), 'foo=bar')
        # content_type without "charset=xxxx"
        self.assertEquals(utils.encode_params({'foo': 'bar'}, 'ba'), 'foo=bar')

    def test_encode_params_charset_utf8(self):
        # charset is using inconsistent casing on purpose, it should still work
        self.assertEquals(utils.encode_params({'f': '€'}, ' CHARset=uTF-8; '),
                          'f=%E2%82%AC')


class make_patternTest(unittest.TestCase):

    def call_FUT(self, obj):
        from webtest.utils import make_pattern
        return make_pattern(obj)

    def test_make_pattern_None(self):
        self.assertEquals(self.call_FUT(None), None)

    def test_make_pattern_regex(self):
        regex = re.compile(r'foobar')
        self.assertEquals(self.call_FUT(regex), regex.search)

    def test_make_pattern_function(self):
        func = lambda x: x
        self.assertEquals(self.call_FUT(func), func)

    def test_make_pattern_bytes(self):
        # if we pass a string, it will get compiled into a regex
        # that we can later call and match a string
        self.assertEqual(self.call_FUT('a')('a').string, 'a')

    def test_make_pattern_invalid(self):
        self.assertRaises(ValueError, self.call_FUT, 0)


class parse_attrsTest(unittest.TestCase):

    def call_FUT(self, obj):
        from webtest.utils import parse_attrs
        return parse_attrs(obj)

    def test_single_quote(self):
        self.assertEqual(self.call_FUT("href='foo'"),
                         {'href': 'foo'})

    def test_double_quote(self):
        self.assertEqual(self.call_FUT('href="foo"'),
                         {'href': 'foo'})

    def test_empty(self):
        self.assertEqual(self.call_FUT('href=""'),
                         {'href': ''})

    def test_two_attrs_double_quote(self):
        self.assertEqual(self.call_FUT('href="foo" id="bar"'),
                         {'href': 'foo', 'id': 'bar'})

    def test_two_attrs_mixed_quotes(self):
        self.assertEqual(self.call_FUT("href='foo' id=\"bar\" "),
                         {'href': 'foo', 'id': 'bar'})

    def test_two_attrs_single_quote(self):
        self.assertEqual(self.call_FUT("href='foo' id='bar' "),
                         {'href': 'foo', 'id': 'bar'})

    def test_single_quote_escape(self):
        self.assertEqual(self.call_FUT("tag='foo\"'"),
                         {'tag': 'foo"'})

    def test_unescape_html_entities(self):
        self.assertEqual(self.call_FUT('value="&lt;&gt;&amp;&quot;&#123;"'),
                         {'value': '<>&"{'})

    def test_unescape_symbol_sum(self):
        self.assertEqual(self.call_FUT('value="&sum;"'),
                         {'value': "∑"})

    def test_unescape_symbol_euro(self):
        self.assertEqual(self.call_FUT('value="&#x20ac;"'),
                         {'value': "€"})


class stringifyTest(unittest.TestCase):

    def test_stringify_text(self):
        self.assertEquals(utils.stringify("foo"), "foo")

    def test_stringify_binary(self):
        self.assertEquals(utils.stringify(b"foo"), "foo")

    def test_stringify_other(self):
        self.assertEquals(utils.stringify(123), "123")


class json_methodTest(unittest.TestCase):

    class MockTestApp(object):
        """Mock TestApp used to test the json_object decorator."""
        from webtest.utils import json_method
        foo_json = json_method('FOO')

        def _gen_request(self, method, url, **kw):
            return (method, url, kw)

    mock = MockTestApp()

    def test_json_method_request_calls(self):
        from webtest.utils import NoDefault
        # no params
        self.assertEquals(self.mock.foo_json('url', params=NoDefault, c='c'),
                          ('FOO', 'url', {'content_type': 'application/json',
                                          'c': 'c',
                                          'params': NoDefault,
                                          'upload_files': None}))
        # params dumped to json
        self.assertEquals(self.mock.foo_json('url', params={'a': 'b'}, c='c'),
                          ('FOO', 'url', {'content_type': 'application/json',
                                          'c': 'c',
                                          'params': dumps({'a': 'b'}),
                                          'upload_files': None}))

    def test_json_method_doc(self):
        self.assertIn('FOO request', self.mock.foo_json.__doc__)
        self.assertIn('TestApp.foo', self.mock.foo_json.__doc__)

    def test_json_method_name(self):
        self.assertEqual(self.mock.foo_json.__name__, 'foo_json')
