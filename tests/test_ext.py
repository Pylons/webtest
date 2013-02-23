# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from .compat import unittest
from webtest import ext


class TestSelenium(unittest.TestCase):

    def test_raises(self):
        self.assertRaises(ImportError, ext.casperjs)
