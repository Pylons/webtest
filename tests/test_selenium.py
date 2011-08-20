# -*- coding: utf-8 -*-
import os
import webob
import webtest
from webob import exc
from webtest import sel
import unittest2 as unittest

files = os.path.dirname(__file__)

def application(environ, start_response):
    req = webob.Request(environ)
    resp = webob.Response()
    if req.method == 'GET':
        filename = os.path.join(files, 'html', req.path_info.strip('/') or 'index.html')
        print filename
        if os.path.isfile(filename):
            kw = dict(message=req.params.get('message', ''),
                      redirect=req.params.get('redirect', ''))
            resp.unicode_body = unicode(open(filename).read()) % kw
            _, ext = os.path.splitext(filename)
            if ext == '.html':
                resp.content_type = 'text/html'
            elif ext == '.js':
                resp.content_type = 'text/javascript'
            elif ext == '.json':
                resp.content_type = 'application/json'
    else:
        redirect = req.params.get('redirect', '')
        if redirect:
            resp = exc.HTTPFound(location=redirect)
        else:
            resp.body = req.body
    return resp(environ, start_response)

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = webtest.TestApp(application)

    def test_webtest(self):
        resp = self.app.get('/', {'redirect': '/message.html?message=submited'})
        resp.mustcontain('It Works!')
        form = resp.forms['myform']

        form['mytext'] = 'toto'
        self.assertEqual(form['mytext'].value, 'toto')
        form['myradio'] = 'true'
        self.assertEqual(form['myradio'].value, 'true')
        form['mycheckbox'] = 'true'
        self.assertEqual(form['mycheckbox'].value, 'true')
        form['myselect'] = 'value2'
        self.assertEqual(form['myselect'].value, 'value2')
        form['mymultiselect'] = ['value1', 'value3']
        self.assertEqual(form['mymultiselect'].value, ['value1', 'value3'])

        resp = form.submit(name='go')
        resp.mustcontain(no='Form submited')
        resp = resp.follow()
        resp.mustcontain('<pre>submited</pre>')

    @sel.with_selenium(commands=('*googlechrome',), close=False)
    def test_selenium(self):
        resp = self.app.get('/', {'redirect': '/message.html?message=submited'})
        resp.mustcontain('It Works!')
        form = resp.forms['myform']
        form['mytext'] = 'toto'
        self.assertEqual(form['mytext'].value, 'toto')
        form['myradio'] = 'true'
        self.assertEqual(form['myradio'].value, 'true')
        form['mycheckbox'] = 'true'
        self.assertEqual(form['mycheckbox'].value, 'true')
        form['myselect'] = 'value2'
        self.assertEqual(form['myselect'].value, 'value2')
        form['mymultiselect'] = ['value1', 'value3']
        self.assertEqual(form['mymultiselect'].value, ['value1', 'value3'])

        # there is an ajax hook on the page
        resp = form.submit(name='go', timeout=0)
        resp.mustcontain('Form submited')

        # but we can submit the form to get the non-javascript behavior
        resp = form.submit()
        resp = resp.follow()
        resp.mustcontain('<pre>submited</pre>')

