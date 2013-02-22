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
from webtest.compat import to_bytes
from webtest.forms import NoValue
from tests.compat import unittest
from tests.compat import u


PAGE_CONTENT = b'''
<html>
    <head><title>Page without form</title></head>
    <body>
        <form method="POST" id="second_form">
            <select name="select">
                <option value="value1">Value 1</option>
                <option value="value2" selected>Value 2</option>
                <option value="value3">Value 3</option>
            </select>
            <input type="file" name="file" />
            <input type="submit" name="submit" />
        </form>
    </body>
</html>
'''


class TestForms(unittest.TestCase):
    def test_set_submit_field(self):
        form = webtest.Form(None, PAGE_CONTENT)
        self.assertRaises(
            AttributeError,
            form['submit'].value__set,
            'foo'
        )

    def test_force_select(self):
        form = webtest.Form(None, PAGE_CONTENT)
        form['select'].force_value('notavalue')
        form['select'].value__set('value3')

        assert form['select']._forced_value is NoValue
        assert form['select'].value == 'value3'
        assert form['select'].selectedIndex == 2

    def test_form_select(self):
        form = webtest.Form(None, PAGE_CONTENT)
        form.select('select', 'value1')

        assert form['select'].value == 'value1'

    def test_get_field_by_index(self):
        form = webtest.Form(None, PAGE_CONTENT)
        self.assertEqual(form['select'],
                         form.get('select', index=0))

    def test_get_non_exist_fields(self):
        form = webtest.Form(None, PAGE_CONTENT)
        self.assertRaises(AssertionError, form.get, 'nonfield')

    def test_get_non_exist_fields_with_default(self):
        form = webtest.Form(None, PAGE_CONTENT)
        value = form.get('nonfield', default=1)
        self.assertEqual(value, 1)

    def test_upload_fields(self):
        form = webtest.Form(None, PAGE_CONTENT)
        fu = webtest.Upload(__file__)
        form['file'] = fu
        self.assertEqual(form.upload_fields(),
                         [['file', __file__]])

    def test_repr(self):
        form = webtest.Form(None, PAGE_CONTENT)
        self.assertTrue(repr(form).startswith('<Form id='))


def no_form_app(environ, start_response):
    status = b"200 OK"
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
    status = b"200 OK"
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


def input_app(environ, start_response):
    Request(environ)
    status = b"200 OK"
    body = to_bytes(
"""
<html>
    <head><title>form page</title></head>
    <body>
        <form method="POST" id="text_input_form">
            <input name="foo" type="text" value="bar">
            <input name="button" type="submit" value="text">
        </form>
        <form method="POST" id="radio_input_form">
            <input name="foo" type="radio" value="bar">
            <input name="foo" type="radio" value="baz" checked>
            <input name="button" type="submit" value="radio">
        </form>
        <form method="POST" id="checkbox_input_form">
            <input name="foo" type="checkbox" value="bar" checked>
            <input name="button" type="submit" value="text">
        </form>
        <form method="POST" id="textarea_input_form">
            <textarea name="textarea">&#39;&#x66;&#x6f;&#x6f;&amp;&#x62;&#x61;&#x72;&#39;</textarea>
        </form>
    </body>
</html>
""")
    headers = [
        ('Content-Type', 'text/html'),
        ('Content-Length', str(len(body)))]
    start_response(status, headers)
    return [body]


def input_app_without_default(environ, start_response):
    Request(environ)
    status = b"200 OK"
    body = to_bytes(
"""
<html>
    <head><title>form page</title></head>
    <body>
        <form method="POST" id="text_input_form">
            <input name="foo" type="text">
            <input name="button" type="submit" value="text">
        </form>
        <form method="POST" id="radio_input_form">
            <input name="foo" type="radio" value="bar">
            <input name="foo" type="radio" value="baz">
            <input name="button" type="submit" value="radio">
        </form>
        <form method="POST" id="checkbox_input_form">
            <input name="foo" type="checkbox" value="bar">
            <input name="button" type="submit" value="text">
        </form>
    </body>
</html>
""")
    headers = [
        ('Content-Type', 'text/html'),
        ('Content-Length', str(len(body)))]
    start_response(status, headers)
    return [body]


def input_unicode_app(environ, start_response):
    Request(environ)
    status = b"200 OK"
    body =\
u("""
<html>
    <head><title>form page</title></head>
    <body>
        <form method="POST" id="text_input_form">
            <input name="foo" type="text" value="Хармс">
            <input name="button" type="submit" value="Сохранить">
        </form>
        <form method="POST" id="radio_input_form">
            <input name="foo" type="radio" value="Хармс">
            <input name="foo" type="radio" value="Блок" checked>
            <input name="button" type="submit" value="Сохранить">
        </form>
        <form method="POST" id="checkbox_input_form">
            <input name="foo" type="checkbox" value="Хармс" checked>
            <input name="button" type="submit" value="Ура">
        </form>
    </body>
</html>
""").encode('utf8')
    headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(body)))]
    start_response(status, headers)
    return [body]


class TestInput(unittest.TestCase):

    def test_input(self):
        app = webtest.TestApp(input_app)
        res = app.get('/')
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.headers['content-type'], 'text/html')
        self.assertEqual(res.content_type, 'text/html')

        form = res.forms['text_input_form']
        self.assertEqual(form['foo'].value, 'bar')
        self.assertEqual(form.submit_fields(), [('foo', 'bar')])

        form = res.forms['radio_input_form']
        self.assertEqual(form['foo'].value, 'baz')
        self.assertEqual(form.submit_fields(), [('foo', 'baz')])

        form = res.forms['checkbox_input_form']
        self.assertEqual(form['foo'].value, 'bar')
        self.assertEqual(form.submit_fields(), [('foo', 'bar')])

    def test_input_unicode(self):
        app = webtest.TestApp(input_unicode_app)
        res = app.get('/')
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.content_type, 'text/html')
        self.assertEqual(res.charset, 'utf-8')

        form = res.forms['text_input_form']
        self.assertEqual(form['foo'].value, u('Хармс'))
        self.assertEqual(form.submit_fields(), [('foo', u('Хармс'))])

        form = res.forms['radio_input_form']
        self.assertEqual(form['foo'].value, u('Блок'))
        self.assertEqual(form.submit_fields(), [('foo', u('Блок'))])

        form = res.forms['checkbox_input_form']
        self.assertEqual(form['foo'].value, u('Хармс'))
        self.assertEqual(form.submit_fields(), [('foo', u('Хармс'))])

    def test_input_no_default(self):
        app = webtest.TestApp(input_app_without_default)
        res = app.get('/')
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.headers['content-type'], 'text/html')
        self.assertEqual(res.content_type, 'text/html')

        form = res.forms['text_input_form']
        self.assertEqual(form['foo'].value, '')
        self.assertEqual(form.submit_fields(), [('foo', '')])

        form = res.forms['radio_input_form']
        self.assertTrue(form['foo'].value is None)
        self.assertEqual(form.submit_fields(), [])

        form = res.forms['checkbox_input_form']
        self.assertTrue(form['foo'].value is None)
        self.assertEqual(form.submit_fields(), [])

    def test_textarea_entities(self):
        app = webtest.TestApp(input_app)
        res = app.get('/')
        form = res.forms.get("textarea_input_form")
        self.assertEqual(form.get("textarea").value, "'foo&bar'")
        self.assertEqual(form.submit_fields(), [('textarea', "'foo&bar'")])


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
            <select id="multiple" name="multiple" multiple="multiple">
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
""" % locals())

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
""" % locals())

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
""") % locals()).encode('utf8')
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
        try:
            single_form.set("single", "984")
            self.fail("not-an-option value error should have been raised")
        except ValueError:
            pass
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
        try:
            multiple_form.set("multiple", ["24", "88"])
            self.fail("not-an-option value error should have been raised")
        except ValueError:
            pass
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
    <head><title>isplay page</title></head>
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
            file_parts.append(b"""
        <p>You selected '""" + filename + b"""'</p>
        <p>with contents: '""" + value + b"""'</p>
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

    def assertFile(self, name, contents, display):
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
        self.assertRaises(ValueError,
            app.post, '/',
            upload_files=[('name', 'filename', 'content', 'extra')]
        )
