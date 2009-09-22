import os.path

from webob import Request
import webtest

def single_upload_file_app(environ, start_response):
    req = Request(environ)
    status = "200 OK"
    if req.method == "GET":
        body =\
"""
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
    else:
        uploaded_files = req.POST.getall("file-field")
        body_head =\
"""
<html>
    <head><title>display page</title></head>
    <body>
"""
        
        file_parts = []
        for uploaded_file in uploaded_files:
            file_parts.append(\
"""        <p>You selected '%(filename)s'</p>
        <p>with contents: '%(value)s'</p>
""" % dict(filename=uploaded_file.filename,
           value=uploaded_file.value))
            
        body_foot =\
"""    </body>
</html>
"""
        body = body_head + "".join(file_parts) + body_foot
    headers = [
        ('Content-Type', 'text/html'),
        ('Content-Length', str(len(body)))]
    start_response(status, headers)
    return [body]

def multiple_upload_file_app(environ, start_response):
    req = Request(environ)
    status = "200 OK"
    if req.method == "GET":
        body =\
"""
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
    else:
        uploaded_file_1 = req.POST.get("file-field-1")
        uploaded_file_2 = req.POST.get("file-field-2")
        uploaded_files = [uploaded_file_1, uploaded_file_2]
        
        body_head =\
"""
<html>
    <head><title>display page</title></head>
    <body>
"""
        
        file_parts = []
        for uploaded_file in uploaded_files:
            file_parts.append(\
"""        <p>You selected '%(filename)s'</p>
        <p>with contents: '%(value)s'</p>
""" % dict(filename=uploaded_file.filename,
           value=uploaded_file.value))
            
        body_foot =\
"""    </body>
</html>
"""
        body = body_head + "".join(file_parts) + body_foot
    headers = [
        ('Content-Type', 'text/html'),
        ('Content-Length', str(len(body)))]
    start_response(status, headers)
    return [body]

def test_file_upload_with_filename_only():
    uploaded_file_name = \
        os.path.join(os.path.dirname(__file__), "__init__.py")
    uploaded_file_contents = file(uploaded_file_name).read()
    
    app = webtest.TestApp(single_upload_file_app)
    res = app.get('/')
    assert res.status_int == 200
    assert res.headers['content-type'] == 'text/html'
    assert res.content_type == 'text/html'
    
    single_form = res.forms["file_upload_form"]
    single_form.set("file-field", (uploaded_file_name,))
    display = single_form.submit("button")
    assert "<p>You selected '%s'</p>" % uploaded_file_name in display, display
    assert "<p>with contents: '%s'</p>" % uploaded_file_contents in display, \
        display

def test_file_upload_with_filename_and_contents():
    uploaded_file_name = \
        os.path.join(os.path.dirname(__file__), "__init__.py")
    uploaded_file_contents = file(uploaded_file_name).read()
    
    app = webtest.TestApp(single_upload_file_app)
    res = app.get('/')
    assert res.status_int == 200
    assert res.headers['content-type'] == 'text/html'
    assert res.content_type == 'text/html'
    
    single_form = res.forms["file_upload_form"]
    single_form.set("file-field",
                    (uploaded_file_name, uploaded_file_contents))
    display = single_form.submit("button")
    assert "<p>You selected '%s'</p>" % uploaded_file_name in display, display
    assert "<p>with contents: '%s'</p>" % uploaded_file_contents in display, \
        display

def test_multiple_file_uploads_with_filename_and_contents():
    uploaded_file1_name = \
        os.path.join(os.path.dirname(__file__), "__init__.py")
    uploaded_file1_contents = file(uploaded_file1_name).read()
    uploaded_file2_name = \
        os.path.join(os.path.dirname(__file__), "test_input.py")
    uploaded_file2_contents = file(uploaded_file2_name).read()
    
    app = webtest.TestApp(multiple_upload_file_app)
    res = app.get('/')
    assert res.status_int == 200
    assert res.headers['content-type'] == 'text/html'
    assert res.content_type == 'text/html'
    
    single_form = res.forms["file_upload_form"]
    single_form.set("file-field-1", (uploaded_file1_name, uploaded_file1_contents))
    single_form.set("file-field-2", (uploaded_file2_name, uploaded_file2_contents))
    display = single_form.submit("button")
    assert "<p>You selected '%s'</p>" % uploaded_file1_name in display, display
    assert "<p>with contents: '%s'</p>" % uploaded_file1_contents in display, \
        display
    assert "<p>You selected '%s'</p>" % uploaded_file2_name in display, display
    assert "<p>with contents: '%s'</p>" % uploaded_file2_contents in display, \
        display
