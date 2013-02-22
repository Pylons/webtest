# -*- coding: utf-8 -*-
from .compat import unittest
from webtest import sel


class TestSelenium(unittest.TestCase):

    def test_raises(self):
        self.assertRaises(ImportError, sel.SeleniumApp)
        self.assertRaises(ImportError, sel.selenium)
