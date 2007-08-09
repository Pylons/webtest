import wsgitest
from wsgitest.debugapp import debug_app

def raises(exc, func, *args, **kw):
    try:
        func(*args, **kw)
    except exc:
        pass
    else:
        raise AssertionError(
            "Expected exception %s from %s"
            % (exc, func))

def test_testing():
    app = wsgitest.TestApp(debug_app)
    res = app.get('/')
    assert res.status_int == 200
    assert res.headers['content-type'] == 'text/plain'
    assert res.content_type == 'text/plain'
    raises(Exception, app.get, '/?error=t')
    raises(wsgitest.AppError, app.get, '/?status=404%20Not%20Found')
    app.get('/?status=404%20Not%20Found', status=404)
    raises(wsgitest.AppError, app.get, '/', status=404)
    res = app.get('/?status=303%20Redirect&header-location=/foo')
    assert res.status_int == 303
    print res.location
    assert res.location == 'http://localhost/foo'
    assert res.headers['location'] == '/foo'
    res = res.follow()
    assert res.request.url == 'http://localhost/foo'
    
