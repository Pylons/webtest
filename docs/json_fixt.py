# -*- coding: utf-8 -*-
from webtest.app import TestApp
from doctest import SKIP
from doctest import ELLIPSIS
from doctest import NORMALIZE_WHITESPACE
from webob import Request
from webob import Response
from six import PY3
import json


def app(environ, start_response):
    req = Request(environ)
    resp = Response(content_type='application/json')
    if req.method == 'GET':
        resp.body = json.dumps(dict(id=1, value='new value'))
    else:
        resp.body = req.body
    return resp(environ, start_response)


def setup_test(test):
    test.globs['app'] = TestApp(app)
    for example in test.examples:
        # only run test with py2 because of dict ordering/output
        if PY3:
            example.options[SKIP] = 1
        else:
            example.options[ELLIPSIS] = 1
            example.options[NORMALIZE_WHITESPACE] = 1

setup_test.__test__ = False
