#coding: utf-8
from __future__ import unicode_literals


import webtest
from webtest.debugapp import debug_app
from webob import Request
from webtest.compat import PY3

from tests.compat import unittest


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
        """
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


class TestResponse(unittest.TestCase):
    def test_repr(self):
        app = webtest.TestApp(debug_app)
        res = app.post('/')
        self.assertEqual(
            repr(res),
            '<200 OK text/plain body="CONTENT_L...0)\\n"/523>'
        )
        res.content_type = None
        self.assertEqual(repr(res), '<200 OK body="CONTENT_L...0)\\n"/523>')

    def test_mustcontains(self):
        app = webtest.TestApp(debug_app)
        res = app.post('/', params='foobar')
        res.mustcontain('foobar')
        self.assertRaises(IndexError, res.mustcontain, 'not found')
        res.mustcontain('foobar', no='not found')
        self.assertRaises(IndexError, res.mustcontain, no='foobar')

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
            'This is baz.',
            app.get('/').click(anchor="<a href='baz/' id='id_baz'>Baz</a>")
        )
        self.assertIn(
            'This is spam.',
            app.get('/').click('Click me!', index=0)
        )
        self.assertIn(
            'Just eggs.',
            app.get('/').click('Click me!', index=1)
        )

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

            # should skip the img tag
            anchor = ".*title='Поэт'.*"
            anchor_re = anchor.encode('utf8')
            self.assertIn('This is baz.', resp.click(anchor=anchor_re))

    def test_click_u(self):
        app = webtest.TestApp(links_app)
        resp = app.get('/utf8/')

        self.assertIn("Тестовая страница", resp)
        self.assertIn('This is foo.', resp.click('Менделеев'))
        self.assertIn('This is baz.', resp.click(anchor=".*title='Поэт'.*"))

    def test_clickbutton(self):
        app = webtest.TestApp(links_app)
        self.assertIn(
            'This is foo.',
            app.get('/').clickbutton(buttonid='button1')
        )
        self.assertRaises(
            IndexError,
            app.get('/').clickbutton, buttonid='button2'
        )
        self.assertRaises(
            IndexError,
            app.get('/').clickbutton, buttonid='button3'
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
