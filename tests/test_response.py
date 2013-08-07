#coding: utf-8
from __future__ import unicode_literals

import zlib


import webtest
from webtest.debugapp import debug_app
from webob import Request
from webob.response import gzip_app_iter
from webtest.compat import PY3

from tests.compat import unittest

import webbrowser


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
                    <button
                        id="button1"
                        onclick="location.href='/foo/'"
                        >Button</button>
                    <button
                        id="button2">Button</button>
                    <button
                        id="button3"
                        onclick="lomistakecation.href='/foo/'"
                        >Button</button>
                </body>
            </html>
            """,

        '/foo/': (
            '<html><body>This is foo. <a href="bar">Bar</a> '
            '</body></html>'
        ),
        '/foo/bar': '<html><body>This is foobar.</body></html>',
        '/bar': '<html><body>This is bar.</body></html>',
        '/baz/': '<html><body>This is baz.</body></html>',
        '/spam/': '<html><body>This is spam.</body></html>',
        '/egg/': '<html><body>Just eggs.</body></html>',

        '/utf8/': """
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
        """,
        '/no_form/': """
            <html>
                <head><title>Page without form</title></head>
                <body>
                    <h1>This is not the form you are looking for</h1>
                </body>
            </html>
        """,
        '/one_forms/': """
            <html>
                <head><title>Page without form</title></head>
                <body>
                    <form method="POST" id="first_form"></form>
                </body>
            </html>
        """,
        '/many_forms/': """
            <html>
                <head><title>Page without form</title></head>
                <body>
                    <form method="POST" id="first_form"></form>
                    <form method="POST" id="second_form"></form>
                </body>
            </html>
        """,
        '/html_in_anchor/': """
            <html>
                <head><title>Page with HTML in an anchor tag</title></head>
                <body>
                    <a href='/foo/'>Foo Bar<span class='baz qux'>Quz</span></a>
                </body>
            </html>
        """,
        '/json/' : '{"foo": "bar"}',
    }

    utf8_paths = ['/utf8/']
    body = responses[req.path_info]
    body = body.encode('utf8')
    headers = [
        ('Content-Type', str('text/html')),
        ('Content-Length', str(len(body)))
    ]
    if req.path_info in utf8_paths:
        headers[0] = ('Content-Type', str('text/html; charset=utf-8'))

    start_response(str(status), headers)
    return [body]


def gzipped_app(environ, start_response):
    status = "200 OK"
    encoded_body = list(gzip_app_iter([b'test']))
    headers = [
        ('Content-Type', str('text/html')),
        ('Content-Encoding', str('gzip')),
    ]

    start_response(str(status), headers)
    return encoded_body


class TestResponse(unittest.TestCase):
    def test_repr(self):
        def _repr(v):
            br = repr(v)
            if len(br) > 18:
                br = br[:10] + '...' + br[-5:]
                br += '/%s' % len(v)

            return br

        app = webtest.TestApp(debug_app)
        res = app.post('/')
        self.assertEqual(
            repr(res),
            '<200 OK text/plain body=%s>' % _repr(res.body)
        )
        res.content_type = None
        self.assertEqual(
            repr(res),
            '<200 OK body=%s>' % _repr(res.body)
        )
        res.location = 'http://pylons.org'
        self.assertEqual(
            repr(res),
            '<200 OK location: http://pylons.org body=%s>' % _repr(res.body)
        )

        res.body = b''
        self.assertEqual(
            repr(res),
            '<200 OK location: http://pylons.org no body>'
        )

    def test_mustcontains(self):
        app = webtest.TestApp(debug_app)
        res = app.post('/', params='foobar')
        res.mustcontain('foobar')
        self.assertRaises(IndexError, res.mustcontain, 'not found')
        res.mustcontain('foobar', no='not found')
        res.mustcontain('foobar', no=['not found', 'not found either'])
        self.assertRaises(IndexError, res.mustcontain, no='foobar')
        self.assertRaises(
            TypeError,
            res.mustcontain, invalid_param='foobar'
        )

    def test_click(self):
        app = webtest.TestApp(links_app)
        self.assertIn('This is foo.', app.get('/').click('Foo'))
        self.assertIn(
            'This is foobar.',
            app.get('/').click('Foo').click('Bar')
        )
        self.assertIn('This is bar.', app.get('/').click('Bar'))
        # should skip non-clickable links
        self.assertIn(
            'This is baz.',
            app.get('/').click('Baz')
        )
        self.assertIn('This is baz.', app.get('/').click(linkid='id_baz'))
        self.assertIn('This is baz.', app.get('/').click(href='baz/'))
        self.assertIn(
            'This is spam.',
            app.get('/').click('Click me!', index=0)
        )
        self.assertIn(
            'Just eggs.',
            app.get('/').click('Click me!', index=1)
        )
        self.assertIn(
            'This is foo.',
            app.get('/html_in_anchor/').click('baz qux')
        )

        def dont_match_anchor_tag():
            app.get('/html_in_anchor/').click('href')
        self.assertRaises(IndexError, dont_match_anchor_tag)

        def multiple_links():
            app.get('/').click('Click me!')
        self.assertRaises(IndexError, multiple_links)

        def invalid_index():
            app.get('/').click('Click me!', index=2)
        self.assertRaises(IndexError, invalid_index)

        def no_links_found():
            app.get('/').click('Ham')
        self.assertRaises(IndexError, no_links_found)

        def tag_inside_script():
            app.get('/').click('Boo')
        self.assertRaises(IndexError, tag_inside_script)

    def test_click_utf8(self):
        app = webtest.TestApp(links_app, use_unicode=False)
        resp = app.get('/utf8/')
        self.assertEqual(resp.charset, 'utf-8')
        if not PY3:
            # No need to deal with that in Py3
            self.assertIn("Тестовая страница".encode('utf8'), resp)
            self.assertIn("Тестовая страница", resp, resp)
            target = 'Менделеев'.encode('utf8')
            self.assertIn('This is foo.', resp.click(target, verbose=True))

    def test_click_u(self):
        app = webtest.TestApp(links_app)
        resp = app.get('/utf8/')

        self.assertIn("Тестовая страница", resp)
        self.assertIn('This is foo.', resp.click('Менделеев'))

    def test_clickbutton(self):
        app = webtest.TestApp(links_app)
        self.assertIn(
            'This is foo.',
            app.get('/').clickbutton(buttonid='button1', verbose=True)
        )
        self.assertRaises(
            IndexError,
            app.get('/').clickbutton, buttonid='button2'
        )
        self.assertRaises(
            IndexError,
            app.get('/').clickbutton, buttonid='button3'
        )

    def test_xml_attribute(self):
        app = webtest.TestApp(links_app)

        resp = app.get('/no_form/')
        self.assertRaises(
            AttributeError,
            getattr,
            resp, 'xml'
        )

        resp.content_type = 'text/xml'
        resp.xml

    def test_lxml_attribute(self):
        app = webtest.TestApp(links_app)
        resp = app.post('/')
        resp.content_type = 'text/xml'
        print(resp.body)
        print(resp.lxml)

    def test_html_attribute(self):
        app = webtest.TestApp(links_app)
        res = app.post('/')
        res.content_type = 'text/plain'
        self.assertRaises(
            AttributeError,
            getattr, res, 'html'
        )

    def test_no_form(self):
        app = webtest.TestApp(links_app)

        resp = app.get('/no_form/')
        self.assertRaises(
            TypeError,
            getattr,
            resp, 'form'
        )

    def test_one_forms(self):
        app = webtest.TestApp(links_app)

        resp = app.get('/one_forms/')
        self.assertEqual(resp.form.id, 'first_form')

    def test_too_many_forms(self):
        app = webtest.TestApp(links_app)

        resp = app.get('/many_forms/')
        self.assertRaises(
            TypeError,
            getattr,
            resp, 'form'
        )

    def test_showbrowser(self):
        def open_new(f):
            self.filename = f

        webbrowser.open_new = open_new
        app = webtest.TestApp(debug_app)
        res = app.post('/')
        res.showbrowser()

    def test_unicode_normal_body(self):
        app = webtest.TestApp(debug_app)
        res = app.post('/')
        self.assertRaises(
            AttributeError,
            getattr, res, 'unicode_normal_body'
        )
        res.charset = 'latin1'
        res.body = 'été'.encode('latin1')
        self.assertEqual(res.unicode_normal_body, 'été')

    def test_testbody(self):
        app = webtest.TestApp(debug_app)
        res = app.post('/')
        res.charset = 'utf8'
        res.body = 'été'.encode('latin1')
        res.testbody

    def test_xml(self):
        app = webtest.TestApp(links_app)

        resp = app.get('/no_form/')
        self.assertRaises(
            AttributeError,
            getattr,
            resp, 'xml'
        )

        resp.content_type = 'text/xml'
        resp.xml

    def test_json(self):
        app = webtest.TestApp(links_app)

        resp = app.get('/json/')
        with self.assertRaises(AttributeError):
            resp.json

        resp.content_type = 'text/json'
        self.assertIn('foo', resp.json)

        resp.content_type = 'application/json'
        self.assertIn('foo', resp.json)

        resp.content_type = 'application/vnd.webtest+json'
        self.assertIn('foo', resp.json)

    def test_unicode(self):
        app = webtest.TestApp(links_app)

        resp = app.get('/')
        if not PY3:
            unicode(resp)

        print(resp.__unicode__())

    def test_content_dezips(self):
        app = webtest.TestApp(gzipped_app)
        resp = app.get('/')
        self.assertEqual(resp.body, b'test')


class TestFollow(unittest.TestCase):

    def get_redirects_app(self, count=1, locations=None):
        """Return an app that issues a redirect ``count`` times"""

        remaining_redirects = [count] # this means "nonlocal"
        if locations is None:
            locations = ['/'] * count

        def app(environ, start_response):
            headers = [('Content-Type', str('text/html'))]

            if remaining_redirects[0] == 0:
                status = "200 OK"
                body = b"done"
            else:
                status = "302 Found"
                body = b''
                nextloc = str(locations.pop(0))
                headers.append(('location', nextloc))
                remaining_redirects[0] -= 1

            headers.append(('Content-Length', str(len(body))))
            start_response(str(status), headers)
            return [body]

        return webtest.TestApp(app)


    def test_follow_with_cookie(self):
        app = webtest.TestApp(debug_app)
        app.get('/?header-set-cookie=foo=bar')
        self.assertEqual(app.cookies['foo'],'bar')
        resp = app.get('/?status=302%20Found&header-location=/')
        resp = resp.follow()
        resp.mustcontain('HTTP_COOKIE: foo=bar')

    def test_follow(self):
        app = self.get_redirects_app(1)
        resp = app.get('/')
        self.assertEqual(resp.status_int, 302)

        resp = resp.follow()
        self.assertEqual(resp.body, b'done')

        # can't follow non-redirect
        self.assertRaises(AssertionError, resp.follow)

    def test_follow_relative(self):
        app = self.get_redirects_app(2, ['hello/foo/', 'bar'])
        resp = app.get('/')
        self.assertEqual(resp.status_int, 302)
        resp = resp.follow()
        self.assertEqual(resp.status_int, 302)
        resp = resp.follow()
        self.assertEqual(resp.body, b'done')
        self.assertEqual(resp.request.url, 'http://localhost/hello/foo/bar')


    def test_follow_twice(self):
        app = self.get_redirects_app(2)
        resp = app.get('/').follow()
        self.assertEqual(resp.status_int, 302)
        resp = resp.follow()
        self.assertEqual(resp.status_int, 200)

    def test_maybe_follow_200(self):
        app = self.get_redirects_app(0)
        resp = app.get('/').maybe_follow()
        self.assertEqual(resp.body, b'done')

    def test_maybe_follow_once(self):
        app = self.get_redirects_app(1)
        resp = app.get('/').maybe_follow()
        self.assertEqual(resp.body, b'done')

    def test_maybe_follow_twice(self):
        app = self.get_redirects_app(2)
        resp = app.get('/').maybe_follow()
        self.assertEqual(resp.body, b'done')

    def test_maybe_follow_infinite(self):
        app = self.get_redirects_app(100000)
        self.assertRaises(AssertionError, app.get('/').maybe_follow)
