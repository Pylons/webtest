from .compat import unittest
from webtest import ext


class TestSelenium(unittest.TestCase):

    def test_raises(self):
        self.assertRaises(ImportError, ext.casperjs)
