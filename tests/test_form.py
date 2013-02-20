# -*- coding: utf-8 -*-

import unittest

import webtest
from webtest.compat import to_bytes

def no_form_app(environ, start_response):
    status = "200 OK"
    body = to_bytes(
"""
<html>
    <head><title>Page without form</title></head>
    <body>
        <h1>This is not the form you are looking for</h1>
    </body>
</html>
""" )

    headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(body)))]
    start_response(status, headers)
    return [body]


def too_many_forms_app(environ, start_response):
    status = "200 OK"
    body = to_bytes(
"""
<html>
    <head><title>Page without form</title></head>
    <body>
        <form method="POST" id="first_form"></form>
        <form method="POST" id="second_form"></form>
    </body>
</html>
""" )

    headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(body)))]
    start_response(status, headers)
    return [body]

class TestForm(unittest.TestCase):

    def test_no_form(self):
        app = webtest.TestApp(no_form_app)
        res = app.get('/')
        
        try:
            res.form
        except TypeError:
            pass
        else:
            raise AssertionError('This call should have thrown an exception')

    def test_too_many_forms(self):
        app = webtest.TestApp(too_many_forms_app)
        res = app.get('/')
        
        try:
            res.form
        except TypeError:
            pass
        else:
            raise AssertionError('This call should have thrown an exception')
