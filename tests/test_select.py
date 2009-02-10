from webob import Request
import webtest

def select_app(environ, start_response):
    req = Request(environ)
    status = "200 OK"
    if req.method == "GET":
        body =\
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
"""
    else:
        select_type = req.POST.get("button")
        if select_type == "single":
            selection = req.POST.get("single")
        elif select_type == "multiple":
            selection = ", ".join(req.POST.getall("multiple"))
        body =\
"""
<html>
    <head><title>display page</title></head>
    <body>
        <p>You submitted the %(select_type)s </p>
        <p>You selected %(selection)s</p>
    </body>
</html>
""" % locals()
    
    headers = [
        ('Content-Type', 'text/html'),
        ('Content-Length', str(len(body)))]
    start_response(status, headers)
    return [body]

def select_app_without_default(environ, start_response):
    req = Request(environ)
    status = "200 OK"
    if req.method == "GET":
        body =\
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
"""
    else:
        select_type = req.POST.get("button")
        if select_type == "single":
            selection = req.POST.get("single")
        elif select_type == "multiple":
            selection = ", ".join(req.POST.getall("multiple"))
        body =\
"""
<html>
    <head><title>display page</title></head>
    <body>
        <p>You submitted the %(select_type)s </p>
        <p>You selected %(selection)s</p>
    </body>
</html>
""" % locals()
    
    headers = [
        ('Content-Type', 'text/html'),
        ('Content-Length', str(len(body)))]
    start_response(status, headers)
    return [body]

def test_single_select():
    app = webtest.TestApp(select_app)
    res = app.get('/')
    assert res.status_int == 200
    assert res.headers['content-type'] == 'text/html'
    assert res.content_type == 'text/html'
    
    single_form = res.forms["single_select_form"]
    assert single_form["single"].value == "5"
    display = single_form.submit("button")
    assert "<p>You selected 5</p>" in display, display
    
    res = app.get('/')
    assert res.status_int == 200
    assert res.headers['content-type'] == 'text/html'
    assert res.content_type == 'text/html'
    
    single_form = res.forms["single_select_form"]
    assert single_form["single"].value == "5"
    single_form.set("single", "6")
    assert single_form["single"].value == "6"
    display = single_form.submit("button")
    assert "<p>You selected 6</p>" in display, display

def test_single_select_forced_value():
    app = webtest.TestApp(select_app)
    res = app.get('/')
    assert res.status_int == 200
    assert res.headers['content-type'] == 'text/html'
    assert res.content_type == 'text/html'
    
    single_form = res.forms["single_select_form"]
    assert single_form["single"].value == "5"
    try:
        single_form.set("single", "984")
        assert False, "not-an-option value error should have been raised"
    except ValueError, exc:
        pass
    single_form["single"].force_value("984")
    assert single_form["single"].value == "984"
    display = single_form.submit("button")
    assert "<p>You selected 984</p>" in display, display

def test_single_select_no_default():
    app = webtest.TestApp(select_app_without_default)
    res = app.get('/')
    assert res.status_int == 200
    assert res.headers['content-type'] == 'text/html'
    assert res.content_type == 'text/html'
    
    single_form = res.forms["single_select_form"]
    assert single_form["single"].value == "4"
    display = single_form.submit("button")
    assert "<p>You selected 4</p>" in display, display
    
    res = app.get('/')
    assert res.status_int == 200
    assert res.headers['content-type'] == 'text/html'
    assert res.content_type == 'text/html'
    
    single_form = res.forms["single_select_form"]
    assert single_form["single"].value == "4"
    single_form.set("single", "6")
    assert single_form["single"].value == "6"
    display = single_form.submit("button")
    assert "<p>You selected 6</p>" in display, display

def test_multiple_select():
    app = webtest.TestApp(select_app)
    res = app.get('/')
    assert res.status_int == 200
    assert res.headers['content-type'] == 'text/html'
    assert res.content_type == 'text/html'
    
    multiple_form = res.forms["multiple_select_form"]
    assert multiple_form["multiple"].value == ['8', '11'],\
        multiple_form["multiple"].value
    display = multiple_form.submit("button")
    assert "<p>You selected 8, 11</p>" in display, display
    
    res = app.get('/')
    assert res.status_int == 200
    assert res.headers['content-type'] == 'text/html'
    assert res.content_type == 'text/html'
    
    multiple_form = res.forms["multiple_select_form"]
    assert multiple_form["multiple"].value == ["8", "11"],\
        multiple_form["multiple"].value
    multiple_form.set("multiple", ["9"])
    assert multiple_form["multiple"].value == ["9"],\
        multiple_form["multiple"].value
    display = multiple_form.submit("button")
    assert "<p>You selected 9</p>" in display, display

def test_multiple_select_forced_values():
    app = webtest.TestApp(select_app)
    res = app.get('/')
    assert res.status_int == 200
    assert res.headers['content-type'] == 'text/html'
    assert res.content_type == 'text/html'
    
    multiple_form = res.forms["multiple_select_form"]
    assert multiple_form["multiple"].value == ["8", "11"],\
        multiple_form["multiple"].value
    try:
        multiple_form.set("multiple", ["24", "88"])
        assert False, "not-an-option value error should have been raised"
    except ValueError, exc:
        pass
    multiple_form["multiple"].force_value(["24", "88"])
    assert multiple_form["multiple"].value == ["24", "88"],\
        multiple_form["multiple"].value
    display = multiple_form.submit("button")
    assert "<p>You selected 24, 88</p>" in display, display

def test_multiple_select_no_default():
    app = webtest.TestApp(select_app_without_default)
    res = app.get('/')
    assert res.status_int == 200
    assert res.headers['content-type'] == 'text/html'
    assert res.content_type == 'text/html'
    
    multiple_form = res.forms["multiple_select_form"]
    assert multiple_form["multiple"].value is None,\
        repr(multiple_form["multiple"].value)
    display = multiple_form.submit("button")
    assert "<p>You selected </p>" in display, display
    
    res = app.get('/')
    assert res.status_int == 200
    assert res.headers['content-type'] == 'text/html'
    assert res.content_type == 'text/html'
    
    multiple_form = res.forms["multiple_select_form"]
    assert multiple_form["multiple"].value is None,\
        multiple_form["multiple"].value
    multiple_form.set("multiple", ["9"])
    assert multiple_form["multiple"].value == ["9"],\
        multiple_form["multiple"].value
    display = multiple_form.submit("button")
    assert "<p>You selected 9</p>" in display, display

