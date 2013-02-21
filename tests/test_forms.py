# -*- coding: utf-8 -*-

from compat import unittest

import webtest

class TestForms(unittest.TestCase):
    def test_set_submit_field(self):
        form = webtest.Form(None, '''
<html>
    <head><title>Page without form</title></head>
    <body>
        <form method="POST" id="second_form">
            <input type="submit" name="submit" />
        </form>
    </body>
</html>
''')
        self.assertRaises(
            AttributeError,
            form['submit'].value__set,
            'foo'
        )

