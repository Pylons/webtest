# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from webtest.debugapp import DebugApp
from tests.compat import unittest
from base64 import b64decode
from webtest.compat import to_bytes

import webtest


class TestAuthorization(unittest.TestCase):

    def callFUT(self):
        return webtest.TestApp(DebugApp())

    def test_basic_authorization(self):
        app = self.callFUT()
        authorization = ('Basic', ['gawel', 'passwd'])
        app.authorization = authorization

        self.assertIn('HTTP_AUTHORIZATION', app.extra_environ)
        self.assertEquals(app.authorization, authorization)

        resp = app.get('/')
        resp.mustcontain('HTTP_AUTHORIZATION: Basic Z2F3ZWw6cGFzc3dk')
        header = resp.request.environ['HTTP_AUTHORIZATION']
        self.assertTrue(header.startswith('Basic '))
        authtype, value = header.split(' ')
        auth = (authtype,
                b64decode(to_bytes(value)).decode('latin1').split(':'))
        self.assertEquals(authorization, auth)

        app.authorization = None
        self.assertNotIn('HTTP_AUTHORIZATION', app.extra_environ)

    def test_bearer_authorization(self):
        app = self.callFUT()
        authorization = ('Bearer', '2588409761fcfa3e378bff4fb766e2e2')
        app.authorization = authorization

        self.assertIn('HTTP_AUTHORIZATION', app.extra_environ)
        self.assertEquals(app.authorization, authorization)

        resp = app.get('/')
        resp.mustcontain('HTTP_AUTHORIZATION: Bearer 2588409761fcfa3e378bff4fb766e2e2')
        header = resp.request.environ['HTTP_AUTHORIZATION']
        self.assertTrue(header.startswith('Bearer '))

        app.authorization = None
        self.assertNotIn('HTTP_AUTHORIZATION', app.extra_environ)

    def test_invalid(self):
        app = self.callFUT()
        self.assertRaises(ValueError, app.set_authorization, ())
        self.assertRaises(ValueError, app.set_authorization, '')
        self.assertRaises(ValueError, app.set_authorization, ('Basic', ''))
        self.assertRaises(ValueError, app.set_authorization, ('Basic', ()))
        self.assertRaises(ValueError, app.set_authorization, ('Bearer', ()))
        self.assertRaises(ValueError, app.set_authorization, ('Bearer', []))
