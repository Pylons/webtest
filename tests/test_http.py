# -*- coding: utf-8 -*-
from tests.compat import unittest
from webtest.debugapp import debug_app
from webtest import http


class TestServer(unittest.TestCase):

    def setUp(self):
        self.s = http.StopableWSGIServer.create(debug_app)

    def test_server(self):
        s = self.s
        s.wait()
        self.assertEqual(200,
                http.check_server(s.adj.host, s.adj.port,
                                  '/__application__'))
        self.assertEqual(200,
                http.check_server(s.adj.host, s.adj.port,
                                  '/__file__?__file__=' + __file__))
        self.assertEqual(404,
                http.check_server(s.adj.host, s.adj.port,
                                  '/__file__?__file__=XXX'))

        self.assertEqual(304,
                http.check_server(s.adj.host, s.adj.port,
                                  '/?status=304'))

    def tearDown(self):
        self.s.shutdown()


class TestBrokenServer(unittest.TestCase):

    def test_shutdown_non_running(self):
        host, port = http.get_free_port()
        s = http.StopableWSGIServer(debug_app, host=host, port=port)
        self.assertFalse(s.wait(retries=1))
        self.assertTrue(s.shutdown())


class TestClient(unittest.TestCase):

    def test_no_server(self):
        host, port = http.get_free_port()
        self.assertEqual(0, http.check_server(host, port, retries=2))
