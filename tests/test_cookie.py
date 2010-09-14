import webtest
from webob import Request


def cookie_app(environ, start_response):
    req = Request(environ)
    status = '200 OK'
    body = '<html><body><a href="/go/">go</a></body></html>'
    headers = [
        ('Content-Type', 'text/html'),
        ('Content-Length', str(len(body))),
    ]
    if req.path_info != '/go/':
        headers.extend([
            ('Set-Cookie', 'spam=eggs'),
            ('Set-Cookie', 'foo="bar;baz"'),
        ])
    start_response(status, headers)
    return [body]


def test_cookies():
    app = webtest.TestApp(cookie_app)
    assert not app.cookies, 'App should initially contain no cookies'
    res = app.get('/')
    cookies = app.cookies
    assert cookies, 'Response should have set cookies'
    assert cookies['spam'] == 'eggs'
    assert cookies['foo'] == 'bar;baz'


def test_preserve_cookies():
    app = webtest.TestApp(cookie_app)
    res = app.get('/')
    assert app.cookies
    go_page = res.click('go')
    assert app.cookies


def cookie_app2(environ, start_response):
    status = '200 OK'
    body = ''
    headers = [
        ('Content-Type', 'text/html'),
        ('Content-Length', str(len(body))),
        ('Set-Cookie', 'spam=eggs'),
        ('Set-Cookie', 'foo="bar;baz"'),
    ]
    start_response(status, headers)
    return [body]


def test_cookies2():
    app = webtest.TestApp(cookie_app)
    assert not app.cookies, 'App should initially contain no cookies'

    res = app.get('/')
    assert app.cookies, 'Response should have set cookies'
    assert app.cookies['spam'] == 'eggs'
    assert app.cookies['foo'] == 'bar;baz'
