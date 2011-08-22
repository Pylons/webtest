# -*- coding: utf-8 -*-
import os
import webob
import webtest
from webob import exc
import unittest2 as unittest

files = os.path.dirname(__file__)

def application(environ, start_response):
    req = webob.Request(environ)
    resp = webob.Response()
    if req.method == 'GET':
        filename = req.path_info.strip('/') or 'index.html'
        if filename in ('302',):
            redirect = req.params['redirect']
            resp = exc.HTTPFound(location=redirect)
            return resp(environ, start_response)
        if filename.isdigit():
            resp.status = filename
            filename = 'index.html'
        filename = os.path.join(files, 'html', filename)
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
        form.lint()
        form['mytext'] = 'toto'
        self.assertEqual(form['mytext'].value, 'toto')
        form['myradio'] = 'true'
        self.assertEqual(form['myradio'].value, 'true')
        check = form.get('mycheckbox', index=0)
        check.value = 'true'
        self.assertEqual(check.value, 'true')
        form['myselect'] = 'value2'
        self.assertEqual(form['myselect'].value, 'value2')
        form['mymultiselect'] = ['value1', 'value3']
        self.assertEqual(form['mymultiselect'].value, ['value1', 'value3'])

        resp = form.submit(name='go')
        resp.mustcontain(no='Form submited')
        resp = resp.follow()
        resp.mustcontain('<pre>submited</pre>')

    @webtest.with_selenium(commands=('*googlechrome',))
    def test_selenium(self):
        resp = self.app.get('/', {'redirect': '/message.html?message=submited'})
        resp.mustcontain('It Works!')
        form = resp.forms['myform']
        form.lint()
        form['mytext'] = 'toto'
        self.assertEqual(form['mytext'].value, 'toto')
        form['myradio'] = 'true'
        self.assertEqual(form['myradio'].value, 'true')
        check = form.get('mycheckbox', index=0)
        check.value = 'true'
        self.assertEqual(check.value, 'true')
        form['myselect'] = 'value2'
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


class TestStatus(unittest.TestCase):

    @classmethod
    def setupClass(cls):
        cls.app = webtest.SeleniumApp(application, command='*googlechrome', timeout=6000)

    def test_302(self):
        resp = self.app.get('/302', dict(redirect='/500'))
        self.assertRaises(webtest.AppError, resp.follow)
        resp.follow(status=500)

        resp = self.app.get('/302', dict(redirect='/404.html'))
        self.assertRaises(webtest.AppError, resp.follow)

    def test_404(self):
        self.assertRaises(webtest.AppError, self.app.get, '/404')
        self.app.get('/404', status=404)
        self.assertRaises(webtest.AppError, self.app.get, '/404.html')

    def test_500(self):
        self.assertRaises(webtest.AppError, self.app.get, '/500')
        self.app.get('/500', status=500)

    @classmethod
    def teardownClass(cls):
        cls.app.close()


class TestJQueryUI(unittest.TestCase):

    @classmethod
    def setupClass(cls):
        cls.app = webtest.SeleniumApp(url='http://jqueryui.com/', command='*googlechrome', timeout=6000)

    def setUp(self):
        self.resp = self.app.get('http://jqueryui.com/demos/')

    def test_autocomplete(self):
        resp = self.resp.click('Autocomplete')
        field = resp.doc.xpath('//input[@id="tags"]')
        field.focus()
        field.type('a')
        if self.app.chrome:
            field.typeKeys(r'\40')
        item = resp.doc.xpath('//ul[@role="listbox"]//a[.="AppleScript"]')
        item.wait()

    def test_datepicker(self):
        resp = self.resp.click('Datepicker')
        field = resp.doc.datepicker
        field.focus()
        day = resp.doc.link('16')
        day.wait().click()
        self.assertIn('/16/', field.value)

    def test_dialog(self):
        resp = self.resp.click('Dialog')
        close = resp.doc.xpath('//div[@role="dialog"]//span[.="close"]')
        close.wait().click()
        resp.doc.link('Modal form').click()
        resp.doc.button('Create new user').wait().click()
        form = resp.form
        form['name'] = 'Gael'
        form['email'] = 'gael@gawel.org'
        create = resp.doc.button('Create an account')
        create.click()
        pwd = form['password']
        self.assertTrue(pwd.hasClass('ui-state-error'))
        pwd.value = 'pwd'
        create.click()
        resp.mustcontain('Length of password must be between 5 and 16.')
        pwd.value = 'passwd'
        create.click()
        resp.mustcontain('<td>Gael</td>')

    def test_dropable(self):
        resp = self.resp.click('Droppable')
        draggable = resp.doc.draggable
        droppable = resp.doc.droppable
        self.assertFalse(droppable.hasClass('ui-state-highlight'))
        draggable.dragAndDropToObject(droppable)
        self.assertTrue(droppable.hasClass('ui-state-highlight'))

        resp.doc.link('Shopping Cart').click()
        cart = resp.doc.css('#cart ol.ui-droppable')
        cart.wait()
        item = resp.doc.xpath('//li[.="Lolcat Shirt"]')
        self.assertNotIn(item, cart)
        item.dragAndDropToObject(cart)
        self.assertIn(item, cart)

    @classmethod
    def teardownClass(cls):
        cls.app.close()

TestJQueryUI = webtest.with_selenium()(TestJQueryUI)
