# -*- coding: utf-8 -*-
from doctest import NORMALIZE_WHITESPACE
from doctest import ELLIPSIS
from doctest import SKIP
from webtest import TestApp
from webob import Request
from webob import Response
import json
import six
import sys


def application(environ, start_response):
    req = Request(environ)
    if req.path_info.endswith('.html'):
        content_type = 'text/html'
        body = six.b('<html><body><div id="content">hey!</div></body>')
    elif req.path_info.endswith('.xml'):
        content_type = 'text/xml'
        body = six.b('<xml><message>hey!</message></xml>')
    elif req.path_info.endswith('.json'):
        content_type = 'application/json'
        body = json.dumps({"a": 1, "b": 2})
    resp = Response(body, content_type=content_type)
    return resp(environ, start_response)


def setup_test(test):
    ver = sys.version_info[:2]
    test.globs.update(app=TestApp(application))
    for example in test.examples:
        if "'xml'" in example.want and ver == (2, 6):
            # minidom node do not render the same in 2.6
            example.options[SKIP] = 1
        else:
            example.options[ELLIPSIS] = 1
            example.options[NORMALIZE_WHITESPACE] = 1

setup_test.__test__ = False
