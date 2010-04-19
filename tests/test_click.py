#coding: utf-8
import webtest
from webtest import _parse_attrs
from webob import Request
from tests.test_testing import raises

def links_app(environ, start_response):
    req = Request(environ)
    status = "200 OK"
    responses = {
       '/': """
            <html>
                <head><title>page with links</title></head>
                <body>
                    <a href="/foo/">Foo</a>
                    <a href='bar'>Bar</a>
                    <a href='baz/' id='id_baz'>Baz</a>
                    <a href='#' id='fake_baz'>Baz</a>
                    <a href='javascript:alert("123")' id='js_baz'>Baz</a>
                    <script>
                        var link = "<a href='/boo/'>Boo</a>";
                    </script>
                    <a href='/spam/'>Click me!</a>
                    <a href='/egg/'>Click me!</a>
                </body>
            </html>
            """,

       '/foo/': '<html><body>This is foo. <a href="bar">Bar</a> </body></html>',
       '/foo/bar': '<html><body>This is foobar.</body></html>',
       '/bar': '<html><body>This is bar.</body></html>',
       '/baz/': '<html><body>This is baz.</body></html>',
       '/spam/': '<html><body>This is spam.</body></html>',
       '/egg/': '<html><body>Just eggs.</body></html>',

       '/utf8/': u"""
            <html>
                <head><title>Тестовая страница</title></head>
                <body>
                    <a href='/foo/'>Менделеев</a>
                    <a href='/baz/' title='Поэт'>Пушкин</a>
                    <img src='/egg/' title='Поэт'>
                    <script>
                        var link = "<a href='/boo/'>Злодейская ссылка</a>";
                    </script>
                </body>
            </html>
            """.encode('utf8'),
    }

    utf8_paths = ['/utf8/']
    body = responses[req.path_info]
    headers = [
        ('Content-Type', 'text/html'),
        ('Content-Length', str(len(body)))
    ]
    if req.path_info in utf8_paths:
        headers[0] = ('Content-Type', 'text/html; charset=utf-8')

    start_response(status, headers)
    return [body]


def test_click():
    app = webtest.TestApp(links_app)
    assert 'This is foo.' in app.get('/').click('Foo')
    assert 'This is foobar.' in app.get('/').click('Foo').click('Bar')
    assert 'This is bar.' in app.get('/').click('Bar')
    assert 'This is baz.' in app.get('/').click('Baz') # should skip non-clickable links
    assert 'This is baz.' in app.get('/').click(linkid='id_baz')
    assert 'This is baz.' in app.get('/').click(href='baz/')
    assert 'This is baz.' in app.get('/').click(anchor="<a href='baz/' id='id_baz'>Baz</a>")
    assert 'This is spam.' in app.get('/').click('Click me!', index=0)
    assert 'Just eggs.' in app.get('/').click('Click me!', index=1)

    def multiple_links():
        app.get('/').click('Click me!')
    raises(IndexError, multiple_links)

    def invalid_index():
        app.get('/').click('Click me!', index=2)
    raises(IndexError, invalid_index)

    def no_links_found():
        app.get('/').click('Ham')
    raises(IndexError, no_links_found)

    def tag_inside_script():
        app.get('/').click('Boo')
    raises(IndexError, tag_inside_script)


def test_click_utf8():
    app = webtest.TestApp(links_app, use_unicode=False)
    resp = app.get('/utf8/')
    assert resp.charset == 'utf-8'
    assert u"Тестовая страница".encode('utf8') in resp
    assert u"Тестовая страница" in resp
    assert 'This is foo.' in resp.click(u'Менделеев'.encode('utf8'))

    # should skip the img tag
    anchor_re = u".*title='Поэт'.*".encode('utf8')
    assert 'This is baz.' in resp.click(anchor=anchor_re)


def test_click_unicode():
    app = webtest.TestApp(links_app)
    resp = app.get('/utf8/')

    assert u"Тестовая страница" in resp
    assert 'This is foo.' in resp.click(u'Менделеев')
    assert 'This is baz.' in resp.click(anchor=u".*title='Поэт'.*")


def test_parse_attrs():
    assert _parse_attrs("href='foo'") == {'href': 'foo'}
    assert _parse_attrs('href="foo"') == {'href': 'foo'}
    assert _parse_attrs('href=""') == {'href': ''}
    assert _parse_attrs('href="foo" id="bar"') == {'href': 'foo', 'id': 'bar'}
    assert _parse_attrs('href="foo" id="bar"') == {'href': 'foo', 'id': 'bar'}
    assert _parse_attrs("href='foo' id=\"bar\" ") == {'href': 'foo', 'id': 'bar'}
    assert _parse_attrs("href='foo' id='bar' ") == {'href': 'foo', 'id': 'bar'}
    assert _parse_attrs("tag='foo\"'") == {'tag': 'foo"'}
