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
        form.select('select','value1')

        assert form['select'].value == 'value1'
 

