# -*- coding: utf-8 -*-

from tests.compat import unittest

import webtest
from webtest.forms import NoValue

PAGE_CONTENT = '''
<html>
    <head><title>Page without form</title></head>
    <body>
        <form method="POST" id="second_form">
            <select name="select">
                <option value="value1">Value 1</option>
                <option value="value2" selected>Value 2</option>
                <option value="value3">Value 3</option>
            </select>
            <input type="file" name="file" />
            <input type="submit" name="submit" />
        </form>
    </body>
</html>
'''


class TestForms(unittest.TestCase):
    def test_set_submit_field(self):
        form = webtest.Form(None, PAGE_CONTENT)
        self.assertRaises(
            AttributeError,
            form['submit'].value__set,
            'foo'
        )

    def test_force_select(self):
        form = webtest.Form(None, PAGE_CONTENT)
        form['select'].force_value('notavalue')
        form['select'].value__set('value3')

        assert form['select']._forced_value is NoValue
        assert form['select'].value == 'value3'
        assert form['select'].selectedIndex == 2

    def test_form_select(self):
        form = webtest.Form(None, PAGE_CONTENT)
        form.select('select', 'value1')

        assert form['select'].value == 'value1'

    def test_get_field_by_index(self):
        form = webtest.Form(None, PAGE_CONTENT)
        self.assertEqual(form['select'],
                         form.get('select', index=0))

    def test_get_non_exist_fields(self):
        form = webtest.Form(None, PAGE_CONTENT)
        self.assertRaises(AssertionError, form.get, 'nonfield')

    def test_get_non_exist_fields_with_default(self):
        form = webtest.Form(None, PAGE_CONTENT)
        value = form.get('nonfield', default=1)
        self.assertEqual(value, 1)

    def test_upload_fields(self):
        form = webtest.Form(None, PAGE_CONTENT)
        fu = webtest.Upload(__file__)
        form['file'] = fu
        self.assertEqual(form.upload_fields(),
                         [['file', __file__]])

    def test_repr(self):
        form = webtest.Form(None, PAGE_CONTENT)
        self.assertTrue(repr(form).startswith('<Form id='))
