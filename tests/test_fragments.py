import webob

import webtest
from webtest.debugapp import debug_app

def raises(exc, func, *args, **kw):
    try:
        func(*args, **kw)
    except exc:
        pass
    else:
        raise AssertionError(
            "Expected exception %s from %s"
            % (exc, func))

def test_url_without_fragments():
    app = webtest.TestApp(debug_app)
    res = app.get('http://localhost/')
    assert res.status_int == 200

def test_url_with_fragments():
    app = webtest.TestApp(debug_app)
    res = app.get('http://localhost/#ananchor')
    assert res.status_int == 200
