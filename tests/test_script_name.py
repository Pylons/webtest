# -*- coding: utf-8 -*-
import webtest
from webob import Request, Response, exc

def application(environ, start_response):
    req = Request(environ)
    if req.path_info == '/redirect':
        req.path_info = '/path'
        resp = exc.HTTPFound(location=req.path)
    else:
        resp = Response()
        resp.body = '<html><body><a href="%s">link</a></body></html>' % req.path
    return resp(environ, start_response)

def test_script_name():
    app = webtest.TestApp(application)

    resp = app.get('/script', extra_environ={'SCRIPT_NAME':'/script'})
    resp.mustcontain('href="/script"')

    resp = app.get('/script/redirect', extra_environ={'SCRIPT_NAME':'/script'})
    assert resp.status_int == 302
    assert resp.location == 'http://localhost/script/path', resp.location

    resp = resp.follow(extra_environ={'SCRIPT_NAME':'/script'})
    resp.mustcontain('href="/script/path"')
    resp = resp.click('link')
    resp.mustcontain('href="/script/path"')

def test_app_script_name():
    app = webtest.TestApp(application, extra_environ={'SCRIPT_NAME':'/script'})
    resp = app.get('/script/redirect')
    assert resp.status_int == 302
    assert resp.location == 'http://localhost/script/path', resp.location

    resp = resp.follow()
    resp.mustcontain('href="/script/path"')
    resp = resp.click('link')
    resp.mustcontain('href="/script/path"')

def test_script_name_doesnt_match():
    app = webtest.TestApp(application)
    resp = app.get('/path', extra_environ={'SCRIPT_NAME':'/script'})
    resp.mustcontain('href="/script/path"')

