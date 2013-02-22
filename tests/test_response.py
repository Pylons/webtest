import webtest
from webtest.debugapp import debug_app

from tests.compat import unittest


class TestResponse(unittest.TestCase):
    def setUp(self):
        self.app = webtest.TestApp(debug_app)

    def test_mustcontains(self):
        res = self.app.post('/', params='foobar')
        res.mustcontain('foobar')
        self.assertRaises(IndexError, res.mustcontain, 'not found')
        res.mustcontain('foobar', no='not found')
        self.assertRaises(IndexError, res.mustcontain, no='foobar')
