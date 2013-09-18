# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os.path
import struct
import sys

import webtest
import six
from six import binary_type
from six import PY3
from webob import Request
from webtest.debugapp import DebugApp
from webtest.compat import to_bytes
from webtest.forms import NoValue, Submit, Upload
from tests.compat import unittest
from tests.compat import u


class TestForms(unittest.TestCase):

    def callFUT(self, filename='form_inputs.html', formid='simple_form'):
        dirname = os.path.join(os.path.dirname(__file__), 'html')
        app = DebugApp(form=os.path.join(dirname, filename), show_form=True)
        resp = webtest.TestApp(app).get('/form.html')
        return resp.forms[formid]

    def test_set_submit_field(self):
        form = self.callFUT()
        self.assertRaises(
            AttributeError,
            form['submit'].value__set,
            'foo'
        )

    def test_button(self):
        form = self.callFUT()
        button = form['button']
        self.assertTrue(isinstance(button, Submit),
                        "<button> without type is a submit button")

    def test_force_select(self):
        form = self.callFUT()
        form['select'].force_value('notavalue')
        form['select'].value__set('value3')

        self.assertTrue(form['select']._forced_value is NoValue,
            "Setting a value after having forced a value should keep a forced"
            " state")
        self.assertEqual(form['select'].value, 'value3',
            "the value should the the one set by value__set")
        self.assertEqual(form['select'].selectedIndex, 2,
            "the value index should be the one set by value__set")

    def test_form_select(self):
        form = self.callFUT()
        form.select('select', 'value1')

        self.assertEqual(form['select'].value, 'value1',
            "when using form.select, the input selected value should be "
            "changed")

    def test_get_field_by_index(self):
        form = self.callFUT()
        self.assertEqual(form['select'],
                         form.get('select', index=0))

    def test_get_unknown_field(self):
        form = self.callFUT()
        self.assertEqual(form['unknown'].value, '')
        form['unknown'].value = '1'
        self.assertEqual(form['unknown'].value, '1')

    def test_get_non_exist_fields(self):
        form = self.callFUT()
        self.assertRaises(AssertionError, form.get, 'nonfield')

    def test_get_non_exist_fields_with_default(self):
        form = self.callFUT()
        value = form.get('nonfield', default=1)
        self.assertEqual(value, 1)

    def test_upload_fields(self):
        form = self.callFUT()
        fu = webtest.Upload(__file__)
        form['file'] = fu
        self.assertEqual(form.upload_fields(),
                         [['file', __file__]])

    def test_repr(self):
        form = self.callFUT()
        self.assertTrue(repr(form).startswith('<Form id='))

    def test_the_bs_node_must_not_change(self):
        form = self.callFUT()
        self.assertEqual(form.text, str(form.html))

    def test_set_multiple_checkboxes(self):
        form = self.callFUT(formid='multiple_checkbox_form')
        form['checkbox'] = [10, 30]

        self.assertEqual(form.get('checkbox', index=0).value, '10')
        self.assertEqual(form.get('checkbox', index=1).value, None)
        self.assertEqual(form.get('checkbox', index=2).value, '30')


class TestResponseFormAttribute(unittest.TestCase):

    def callFUT(self, body):
        app = DebugApp(form=to_bytes(body))
        return webtest.TestApp(app)

    def test_no_form(self):
        app = self.callFUT('<html><body></body></html>')
        res = app.get('/form.html')
        self.assertRaises(TypeError, lambda: res.form)

    def test_too_many_forms(self):
        app = self.callFUT(
            '<html><body><form></form><form></form></body></html>')
        res = app.get('/form.html')
        self.assertRaises(TypeError, lambda: res.form)


class TestInput(unittest.TestCase):

    def callFUT(self, filename='form_inputs.html'):
        dirname = os.path.join(os.path.dirname(__file__), 'html')
        app = DebugApp(form=os.path.join(dirname, filename), show_form=True)
        return webtest.TestApp(app)

    def test_input(self):
        app = self.callFUT()
        res = app.get('/form.html')
        self.assertEqual(res.status_int, 200)
        self.assertTrue(res.content_type.startswith('text/html'))

        form = res.forms['text_input_form']
        self.assertEqual(form['foo'].value, 'bar')
        self.assertEqual(form.submit_fields(), [('foo', 'bar')])

        form = res.forms['radio_input_form']
        self.assertEqual(form['foo'].value, 'baz')
        self.assertEqual(form.submit_fields(), [('foo', 'baz')])

        form = res.forms['checkbox_input_form']
        self.assertEqual(form['foo'].value, 'bar')
        self.assertEqual(form.submit_fields(), [('foo', 'bar')])

        form = res.forms['password_input_form']
        self.assertEqual(form['foo'].value, 'bar')
        self.assertEqual(form.submit_fields(), [('foo', 'bar')])

    def test_input_unicode(self):
        app = self.callFUT('form_unicode_inputs.html')
        res = app.get('/form.html')
        self.assertEqual(res.status_int, 200)
        self.assertTrue(res.content_type.startswith('text/html'))
        self.assertEqual(res.charset.lower(), 'utf-8')

        form = res.forms['text_input_form']
        self.assertEqual(form['foo'].value, u('Хармс'))
        self.assertEqual(form.submit_fields(), [('foo', u('Хармс'))])

        form = res.forms['radio_input_form']
        self.assertEqual(form['foo'].value, u('Блок'))
        self.assertEqual(form.submit_fields(), [('foo', u('Блок'))])

        form = res.forms['checkbox_input_form']
        self.assertEqual(form['foo'].value, u('Хармс'))
        self.assertEqual(form.submit_fields(), [('foo', u('Хармс'))])

        form = res.forms['password_input_form']
        self.assertEqual(form['foo'].value, u('Хармс'))
        self.assertEqual(form.submit_fields(), [('foo', u('Хармс'))])

    def test_input_no_default(self):
        app = self.callFUT('form_inputs_with_defaults.html')
        res = app.get('/form.html')
        self.assertEqual(res.status_int, 200)
        self.assertTrue(res.content_type.startswith('text/html'))

        form = res.forms['text_input_form']
        self.assertEqual(form['foo'].value, '')
        self.assertEqual(form.submit_fields(), [('foo', '')])

        form = res.forms['radio_input_form']
        self.assertTrue(form['foo'].value is None)
        self.assertEqual(form.submit_fields(), [])

        form = res.forms['checkbox_input_form']
        self.assertTrue(form['foo'].value is None)
        self.assertEqual(form.submit_fields(), [])

        form = res.forms['password_input_form']
        self.assertEqual(form['foo'].value, '')
        self.assertEqual(form.submit_fields(), [('foo', '')])

    def test_textarea_entities(self):
        app = self.callFUT()
        res = app.get('/form.html')
        form = res.forms.get("textarea_input_form")
        self.assertEqual(form.get("textarea").value, "'foo&bar'")
        self.assertEqual(form.submit_fields(), [('textarea', "'foo&bar'")])

    def test_textarea_emptyfirstline(self):
        app = self.callFUT()
        res = app.get('/form.html')
        form = res.forms.get("textarea_emptyline_form")
        self.assertEqual(form.get("textarea").value, "aaa")
        self.assertEqual(form.submit_fields(), [('textarea', "aaa")])


class TestFormLint(unittest.TestCase):

    def test_form_lint(self):
        form = webtest.Form(None, '''<form>
        <input type="text" name="field"/>
        </form>''')
        self.assertRaises(AttributeError, form.lint)

        form = webtest.Form(None, '''<form>
        <input type="text" id="myfield" name="field"/>
        </form>''')
        self.assertRaises(AttributeError, form.lint)

        form = webtest.Form(None, '''<form>
        <label for="myfield">my field</label>
        <input type="text" id="myfield" name="field"/>
        </form>''')
        form.lint()

        form = webtest.Form(None, '''<form>
        <label class="field" for="myfield" role="r">my field</label>
        <input type="text" id="myfield" name="field"/>
        </form>''')
        form.lint()


def select_app(environ, start_response):
    req = Request(environ)
    status = b"200 OK"
    if req.method == "GET":
        body = to_bytes(
"""
<html>
    <head><title>form page</title></head>
    <body>
        <form method="POST" id="single_select_form">
            <select id="single" name="single">
                <option value="4">Four</option>
                <option value="5" selected="selected">Five</option>
                <option value="6">Six</option>
                <option value="7">Seven</option>
            </select>
            <input name="button" type="submit" value="single">
        </form>
        <form method="POST" id="multiple_select_form">
            <select id="multiple" name="multiple" multiple>
                <option value="8" selected="selected">Eight</option>
                <option value="9">Nine</option>
                <option value="10">Ten</option>
                <option value="11" selected="selected">Eleven</option>
            </select>
            <input name="button" type="submit" value="multiple">
        </form>
    </body>
</html>
""")
    else:
        select_type = req.POST.get("button")
        if select_type == "single":
            selection = req.POST.get("single")
        elif select_type == "multiple":
            selection = ", ".join(req.POST.getall("multiple"))
        body = to_bytes(
"""
<html>
    <head><title>display page</title></head>
    <body>
        <p>You submitted the %(select_type)s </p>
        <p>You selected %(selection)s</p>
    </body>
</html>
""" % dict(selection=selection, select_type=select_type))

    headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(body)))]
    start_response(status, headers)
    return [body]


def select_app_without_values(environ, start_response):
    req = Request(environ)
    status = b"200 OK"
    if req.method == "GET":
        body = to_bytes(
"""
<html>
    <head><title>form page</title></head>
    <body>
        <form method="POST" id="single_select_form">
            <select id="single" name="single">
                <option>Four</option>
                <option>Five</option>
                <option>Six</option>
                <option>Seven</option>
            </select>
            <input name="button" type="submit" value="single">
        </form>
        <form method="POST" id="multiple_select_form">
            <select id="multiple" name="multiple" multiple="multiple">
                <option>Eight</option>
                <option selected value="Nine">Nine</option>
                <option>Ten</option>
                <option selected>Eleven</option>
            </select>
            <input name="button" type="submit" value="multiple">
        </form>
    </body>
</html>
""")
    else:
        select_type = req.POST.get("button")
        if select_type == "single":
            selection = req.POST.get("single")
        elif select_type == "multiple":
            selection = ", ".join(req.POST.getall("multiple"))
        body = to_bytes(
"""
<html>
    <head><title>display page</title></head>
    <body>
        <p>You submitted the %(select_type)s </p>
        <p>You selected %(selection)s</p>
    </body>
</html>
""" % dict(selection=selection, select_type=select_type))

    headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(body)))]
    start_response(status, headers)
    return [body]


def select_app_without_default(environ, start_response):
    req = Request(environ)
    status = b"200 OK"
    if req.method == "GET":
        body = to_bytes(
"""
<html>
    <head><title>form page</title></head>
    <body>
        <form method="POST" id="single_select_form">
            <select id="single" name="single">
                <option value="4">Four</option>
                <option value="5">Five</option>
                <option value="6">Six</option>
                <option value="7">Seven</option>
            </select>
            <input name="button" type="submit" value="single">
        </form>
        <form method="POST" id="multiple_select_form">
            <select id="multiple" name="multiple" multiple="multiple">
                <option value="8">Eight</option>
                <option value="9">Nine</option>
                <option value="10">Ten</option>
                <option value="11">Eleven</option>
            </select>
            <input name="button" type="submit" value="multiple">
        </form>
    </body>
</html>
""")
    else:
        select_type = req.POST.get("button")
        if select_type == "single":
            selection = req.POST.get("single")
        elif select_type == "multiple":
            selection = ", ".join(req.POST.getall("multiple"))
        body = to_bytes(
"""
<html>
    <head><title>display page</title></head>
    <body>
        <p>You submitted the %(select_type)s </p>
        <p>You selected %(selection)s</p>
    </body>
</html>
""" % dict(selection=selection, select_type=select_type))

    headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(body)))]
    start_response(status, headers)
    return [body]


def select_app_unicode(environ, start_response):
    req = Request(environ)
    status = b"200 OK"
    if req.method == "GET":
        body =\
u("""
<html>
    <head><title>form page</title></head>
    <body>
        <form method="POST" id="single_select_form">
            <select id="single" name="single">
                <option value="ЕКБ">Екатеринбург</option>
                <option value="МСК" selected="selected">Москва</option>
                <option value="СПБ">Санкт-Петербург</option>
                <option value="САМ">Самара</option>
            </select>
            <input name="button" type="submit" value="single">
        </form>
        <form method="POST" id="multiple_select_form">
            <select id="multiple" name="multiple" multiple="multiple">
                <option value="8" selected="selected">Лондон</option>
                <option value="9">Париж</option>
                <option value="10">Пекин</option>
                <option value="11" selected="selected">Бристоль</option>
            </select>
            <input name="button" type="submit" value="multiple">
        </form>
    </body>
</html>
""").encode('utf8')
    else:
        select_type = req.POST.get("button")
        if select_type == "single":
            selection = req.POST.get("single")
        elif select_type == "multiple":
            selection = ", ".join(req.POST.getall("multiple"))
        body = (
u("""
<html>
    <head><title>display page</title></head>
    <body>
        <p>You submitted the %(select_type)s </p>
        <p>You selected %(selection)s</p>
    </body>
</html>
""") % dict(selection=selection, select_type=select_type)).encode('utf8')
    headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(body)))]
    start_response(status, headers)
    if not isinstance(body, binary_type):
        raise AssertionError('Body is not %s' % binary_type)
    return [body]


class TestSelect(unittest.TestCase):

    def test_unicode_select(self):
        app = webtest.TestApp(select_app_unicode)
        res = app.get('/')
        single_form = res.forms["single_select_form"]
        self.assertEqual(single_form["single"].value, u("МСК"))

        display = single_form.submit("button")
        self.assertIn(u("<p>You selected МСК</p>"), display, display)

        res = app.get('/')
        single_form = res.forms["single_select_form"]
        self.assertEqual(single_form["single"].value, u("МСК"))
        single_form.set("single", u("СПБ"))
        self.assertEqual(single_form["single"].value, u("СПБ"))
        display = single_form.submit("button")
        self.assertIn(u("<p>You selected СПБ</p>"), display, display)

    def test_single_select(self):
        app = webtest.TestApp(select_app)
        res = app.get('/')
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.headers['content-type'],
                         'text/html; charset=utf-8')
        self.assertEqual(res.content_type, 'text/html')

        single_form = res.forms["single_select_form"]
        self.assertEqual(single_form["single"].value, "5")
        display = single_form.submit("button")
        self.assertIn("<p>You selected 5</p>", display, display)

        res = app.get('/')
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.headers['content-type'],
                         'text/html; charset=utf-8')
        self.assertEqual(res.content_type, 'text/html')

        single_form = res.forms["single_select_form"]
        self.assertEqual(single_form["single"].value, "5")
        single_form.set("single", "6")
        self.assertEqual(single_form["single"].value, "6")
        display = single_form.submit("button")
        self.assertIn("<p>You selected 6</p>", display, display)

    def test_single_select_forced_value(self):
        app = webtest.TestApp(select_app)
        res = app.get('/')
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.headers['content-type'],
                         'text/html; charset=utf-8')
        self.assertEqual(res.content_type, 'text/html')

        single_form = res.forms["single_select_form"]
        self.assertEqual(single_form["single"].value, "5")
        self.assertRaises(ValueError, single_form.set, "single", "984")
        single_form["single"].force_value("984")
        self.assertEqual(single_form["single"].value, "984")
        display = single_form.submit("button")
        self.assertIn("<p>You selected 984</p>", display, display)

    def test_single_select_no_default(self):
        app = webtest.TestApp(select_app_without_default)
        res = app.get('/')
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.headers['content-type'],
                         'text/html; charset=utf-8')
        self.assertEqual(res.content_type, 'text/html')

        single_form = res.forms["single_select_form"]
        self.assertEqual(single_form["single"].value, "4")
        display = single_form.submit("button")
        self.assertIn("<p>You selected 4</p>", display, display)

        res = app.get('/')
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.headers['content-type'],
                         'text/html; charset=utf-8')
        self.assertEqual(res.content_type, 'text/html')

        single_form = res.forms["single_select_form"]
        self.assertEqual(single_form["single"].value, "4")
        single_form.set("single", 6)
        self.assertEqual(single_form["single"].value, "6")
        display = single_form.submit("button")
        self.assertIn("<p>You selected 6</p>", display, display)

    def test_multiple_select(self):
        app = webtest.TestApp(select_app)
        res = app.get('/')
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.headers['content-type'],
                         'text/html; charset=utf-8')
        self.assertEqual(res.content_type, 'text/html')

        multiple_form = res.forms["multiple_select_form"]
        self.assertEqual(multiple_form["multiple"].value, ['8', '11'],
                         multiple_form["multiple"].value)
        display = multiple_form.submit("button")
        self.assertIn("<p>You selected 8, 11</p>", display, display)

        res = app.get('/')
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.headers['content-type'],
                         'text/html; charset=utf-8')
        self.assertEqual(res.content_type, 'text/html')

        multiple_form = res.forms["multiple_select_form"]
        self.assertEqual(multiple_form["multiple"].value, ["8", "11"],
                         multiple_form["multiple"].value)
        multiple_form.set("multiple", ["9"])
        self.assertEqual(multiple_form["multiple"].value, ["9"],
                         multiple_form["multiple"].value)
        display = multiple_form.submit("button")
        self.assertIn("<p>You selected 9</p>", display, display)

    def test_multiple_select_forced_values(self):
        app = webtest.TestApp(select_app)
        res = app.get('/')
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.headers['content-type'],
                         'text/html; charset=utf-8')
        self.assertEqual(res.content_type, 'text/html')

        multiple_form = res.forms["multiple_select_form"]
        self.assertEqual(multiple_form["multiple"].value, ["8", "11"],
                         multiple_form["multiple"].value)
        self.assertRaises(ValueError, multiple_form.set,
                                      "multiple", ["24", "88"])
        multiple_form["multiple"].force_value(["24", "88"])
        self.assertEqual(multiple_form["multiple"].value, ["24", "88"],
                         multiple_form["multiple"].value)
        display = multiple_form.submit("button")
        self.assertIn("<p>You selected 24, 88</p>", display, display)

    def test_multiple_select_no_default(self):
        app = webtest.TestApp(select_app_without_default)
        res = app.get('/')
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.headers['content-type'],
                         'text/html; charset=utf-8')
        self.assertEqual(res.content_type, 'text/html')

        multiple_form = res.forms["multiple_select_form"]
        self.assertTrue(multiple_form["multiple"].value is None,
                        repr(multiple_form["multiple"].value))
        display = multiple_form.submit("button")
        self.assertIn("<p>You selected </p>", display, display)

        res = app.get('/')
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.headers['content-type'],
                         'text/html; charset=utf-8')
        self.assertEqual(res.content_type, 'text/html')

        multiple_form = res.forms["multiple_select_form"]
        self.assertTrue(multiple_form["multiple"].value is None,
                        multiple_form["multiple"].value)
        multiple_form.set("multiple", ["9"])
        self.assertEqual(multiple_form["multiple"].value, ["9"],
                         multiple_form["multiple"].value)
        display = multiple_form.submit("button")
        self.assertIn("<p>You selected 9</p>", display, display)

    def test_select_no_value(self):
        app = webtest.TestApp(select_app_without_values)
        res = app.get('/')
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.headers['content-type'],
                         'text/html; charset=utf-8')
        self.assertEqual(res.content_type, 'text/html')

        single_form = res.forms["single_select_form"]
        self.assertEqual(single_form["single"].value, "Four")
        display = single_form.submit("button")
        self.assertIn("<p>You selected Four</p>", display, display)

        res = app.get('/')
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.headers['content-type'],
                         'text/html; charset=utf-8')
        self.assertEqual(res.content_type, 'text/html')

        single_form = res.forms["single_select_form"]
        self.assertEqual(single_form["single"].value, "Four")
        single_form.set("single", "Six")
        self.assertEqual(single_form["single"].value, "Six")
        display = single_form.submit("button")
        self.assertIn("<p>You selected Six</p>", display, display)

    def test_multiple_select_no_value(self):
        app = webtest.TestApp(select_app_without_values)
        res = app.get('/')
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.headers['content-type'],
                         'text/html; charset=utf-8')
        self.assertEqual(res.content_type, 'text/html')

        multiple_form = res.forms["multiple_select_form"]
        self.assertEqual(multiple_form["multiple"].value, ["Nine", "Eleven"])
        display = multiple_form.submit("button")
        self.assertIn("<p>You selected Nine, Eleven</p>", display, display)

        res = app.get('/')
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.headers['content-type'],
                         'text/html; charset=utf-8')
        self.assertEqual(res.content_type, 'text/html')

        multiple_form = res.forms["multiple_select_form"]
        self.assertEqual(multiple_form["multiple"].value, ["Nine", "Eleven"])
        multiple_form.set("multiple", ["Nine", "Ten"])
        self.assertEqual(multiple_form["multiple"].value, ["Nine", "Ten"])
        display = multiple_form.submit("button")
        self.assertIn("<p>You selected Nine, Ten</p>", display, display)


class SingleUploadFileApp(object):

    body = b"""
<html>
    <head><title>form page</title></head>
    <body>
        <form method="POST" id="file_upload_form"
              enctype="multipart/form-data">
            <input name="file-field" type="file" />
            <input name="button" type="submit" value="single">
        </form>
    </body>
</html>
"""

    def __call__(self, environ, start_response):
        req = Request(environ)
        status = b"200 OK"
        if req.method == "GET":
            body = self.body
        else:
            body = b"""
<html>
    <head><title>display page</title></head>
    <body>
        """ + self.get_files_page(req) + b"""
    </body>
</html>
"""
        headers = [
            ('Content-Type', 'text/html; charset=utf-8'),
            ('Content-Length', str(len(body)))]
        start_response(status, headers)
        assert(isinstance(body, binary_type))
        return [body]

    def get_files_page(self, req):
        file_parts = []
        uploaded_files = [(k, v) for k, v in req.POST.items() if 'file' in k]
        uploaded_files = sorted(uploaded_files)
        for name, uploaded_file in uploaded_files:
            filename = to_bytes(uploaded_file.filename)
            value = to_bytes(uploaded_file.value, 'ascii')
            content_type = to_bytes(uploaded_file.type, 'ascii')
            file_parts.append(b"""
        <p>You selected '""" + filename + b"""'</p>
        <p>with contents: '""" + value + b"""'</p>
        <p>with content type: '""" + content_type + b"""'</p>
""")
        return b''.join(file_parts)


class UploadBinaryApp(SingleUploadFileApp):

    def get_files_page(self, req):
        uploaded_files = [(k, v) for k, v in req.POST.items() if 'file' in k]
        data = uploaded_files[0][1].value
        if PY3:
            data = struct.unpack(b'255h', data[:510])
        else:
            data = struct.unpack(str('255h'), data)
        return b','.join([to_bytes(str(i)) for i in data])


class MultipleUploadFileApp(SingleUploadFileApp):
    body = b"""
<html>
    <head><title>form page</title></head>
    <body>
        <form method="POST" id="file_upload_form"
              enctype="multipart/form-data">
            <input name="file-field-1" type="file" />
            <input name="file-field-2" type="file" />
            <input name="button" type="submit" value="single">
        </form>
    </body>
</html>
"""


class TestFileUpload(unittest.TestCase):

    def assertFile(self, name, contents, display, content_type=None):
        if isinstance(name, six.binary_type):
            text_name = name.decode('ascii')
        else:
            text_name = name
        self.assertIn("<p>You selected '" + text_name + "'</p>",
                      display, display)
        if isinstance(contents, six.binary_type):
            text_contents = contents.decode('ascii')
        else:
            text_contents = contents
        self.assertIn("<p>with contents: '" + text_contents + "'</p>",
                      display, display)
        if content_type:
            self.assertIn("<p>with content type: '" + content_type + "'</p>",
                          display, display)

    def test_no_uploads_error(self):
        app = webtest.TestApp(SingleUploadFileApp())
        app.get('/').forms["file_upload_form"].upload_fields()

    def test_upload_without_file(self):
        app = webtest.TestApp(SingleUploadFileApp())
        upload_form = app.get('/').forms["file_upload_form"]
        upload_form.submit()

    def test_file_upload_with_filename_only(self):
        uploaded_file_name = os.path.join(os.path.dirname(__file__),
                                          "__init__.py")
        uploaded_file_contents = open(uploaded_file_name).read()
        if PY3:
            uploaded_file_contents = to_bytes(uploaded_file_contents)

        app = webtest.TestApp(SingleUploadFileApp())
        res = app.get('/')
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.headers['content-type'],
                         'text/html; charset=utf-8')
        self.assertEqual(res.content_type, 'text/html')
        self.assertEqual(res.charset, 'utf-8')

        single_form = res.forms["file_upload_form"]
        single_form.set("file-field", (uploaded_file_name,))
        display = single_form.submit("button")
        self.assertFile(uploaded_file_name, uploaded_file_contents, display)

    def test_file_upload_with_filename_and_contents(self):
        uploaded_file_name = os.path.join(os.path.dirname(__file__),
                                            "__init__.py")
        uploaded_file_contents = open(uploaded_file_name).read()
        if PY3:
            uploaded_file_contents = to_bytes(uploaded_file_contents)

        app = webtest.TestApp(SingleUploadFileApp())
        res = app.get('/')
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.headers['content-type'],
                         'text/html; charset=utf-8')
        self.assertEqual(res.content_type, 'text/html')

        single_form = res.forms["file_upload_form"]
        single_form.set("file-field",
                        (uploaded_file_name, uploaded_file_contents))
        display = single_form.submit("button")
        self.assertFile(uploaded_file_name, uploaded_file_contents, display)

    def test_file_upload_with_content_type(self):
        uploaded_file_name = os.path.join(os.path.dirname(__file__),
                                            "__init__.py")
        with open(uploaded_file_name, 'rb') as f:
            uploaded_file_contents = f.read()
        app = webtest.TestApp(SingleUploadFileApp())
        res = app.get('/')
        single_form = res.forms["file_upload_form"]
        single_form["file-field"].value = Upload(uploaded_file_name,
                                                 uploaded_file_contents,
                                                 'text/x-custom-type')
        display = single_form.submit("button")
        self.assertFile(uploaded_file_name, uploaded_file_contents, display,
                        content_type='text/x-custom-type')

    def test_file_upload_binary(self):
        binary_data = struct.pack(str('255h'), *range(0, 255))
        app = webtest.TestApp(UploadBinaryApp())
        res = app.get('/')
        single_form = res.forms["file_upload_form"]
        single_form.set("file-field", ('my_file.dat', binary_data))
        display = single_form.submit("button")
        self.assertIn(','.join([str(n) for n in range(0, 255)]), display)

    def test_multiple_file_uploads_with_filename_and_contents(self):
        uploaded_file1_name = os.path.join(os.path.dirname(__file__),
                                           "__init__.py")
        uploaded_file1_contents = open(uploaded_file1_name).read()
        if PY3:
            uploaded_file1_contents = to_bytes(uploaded_file1_contents)
        uploaded_file2_name = __file__
        uploaded_file2_name = os.path.join(os.path.dirname(__file__), 'html',
                                           "404.html")
        uploaded_file2_contents = open(uploaded_file2_name).read()
        if PY3:
            uploaded_file2_contents = to_bytes(uploaded_file2_contents)

        app = webtest.TestApp(MultipleUploadFileApp())
        res = app.get('/')
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.headers['content-type'],
                         'text/html; charset=utf-8')
        self.assertEqual(res.content_type, 'text/html')

        single_form = res.forms["file_upload_form"]
        single_form.set("file-field-1",
                        (uploaded_file1_name, uploaded_file1_contents))
        single_form.set("file-field-2",
                        (uploaded_file2_name, uploaded_file2_contents))
        display = single_form.submit("button")
        self.assertFile(uploaded_file1_name, uploaded_file1_contents, display)
        self.assertFile(uploaded_file1_name, uploaded_file1_contents, display)

    def test_upload_invalid_content(self):
        app = webtest.TestApp(SingleUploadFileApp())
        res = app.get('/')
        single_form = res.forms["file_upload_form"]
        single_form.set("file-field", ('my_file.dat', 1))
        try:
            single_form.submit("button")
        except ValueError:
            e = sys.exc_info()[1]
            self.assertEquals(
                six.text_type(e),
                u('File content must be %s not %s' % (binary_type, int))
            )

    def test_invalid_uploadfiles(self):
        app = webtest.TestApp(SingleUploadFileApp())
        self.assertRaises(ValueError, app.post, '/', upload_files=[()])
        self.assertRaises(
            ValueError,
            app.post, '/',
            upload_files=[('name', 'filename', 'content', 'extra')]
        )

    def test_goto_upload_files(self):
        app = webtest.TestApp(SingleUploadFileApp())
        resp = app.get('/')
        resp = resp.goto(
            '/',
            method='post',
            upload_files=[('file', 'filename', b'content')]
        )
        resp.mustcontain("<p>You selected 'filename'</p>",
                         "<p>with contents: 'content'</p>")

    def test_post_upload_files(self):
        app = webtest.TestApp(SingleUploadFileApp())
        resp = app.post(
            '/',
            upload_files=[('file', 'filename', b'content')]
        )
        resp.mustcontain("<p>You selected 'filename'</p>",
                         "<p>with contents: 'content'</p>")
