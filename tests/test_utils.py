# -*- coding: utf-8 -*-

import re
import six
import unittest

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
        if six.PY3:
            params = {'foo': '€'}
        else:
            params = {u'foo': u'€'}
        # charset is using inconsistent casing on purpose, it should still work
        self.assertEquals(utils.encode_params(params, ' CHARset=uTF-8; '),
                          'foo=%E2%82%AC')


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


class stringifyTest(unittest.TestCase):

    def test_stringify_text(self):
        if six.PY3:
            value = "foo"
        else:
            value = u"foo"
        self.assertEquals(utils.stringify(value), value)

    def test_stringify_binary(self):
        if six.PY3:
            value = b"foo"
            stringified = "foo"
        else:
            value = "foo"
            stringified = u"foo"
        self.assertEquals(utils.stringify(value), stringified)

    def test_stringify_other(self):
        if six.PY3:
            stringified = "123"
        else:
            stringified = u"123"
        self.assertEquals(utils.stringify(123), stringified)


# TODO: test: json_method
