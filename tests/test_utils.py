# -*- coding: utf-8 -*-

import re
import six
import unittest


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
        if six.PY3:
            value = "∑"
        else:
            value = "∑".decode('utf-8')
        self.assertEqual(self.call_FUT('value="&sum;"'),
                         {'value': value})

    def test_unescape_symbol_euro(self):
        if six.PY3:
            value = "€"
        else:
            value = "€".decode('utf-8')
        self.assertEqual(self.call_FUT('value="&#x20ac;"'),
                         {'value': value})


# TODO: test: CleverCookieDict, json_method, encode_params, stringify
