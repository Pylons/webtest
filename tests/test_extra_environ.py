import webtest
from webtest.debugapp import debug_app


def test_get_extra_environ():
    app = webtest.TestApp(debug_app,
                          extra_environ={'HTTP_ACCEPT_LANGUAGE': 'ru',
                                         'foo': 'bar'})
    res = app.get('http://localhost/')
    assert 'HTTP_ACCEPT_LANGUAGE: ru' in res, res
    assert "foo: 'bar'" in res, res

    res = app.get('http://localhost/', extra_environ={'foo': 'baz'})
    assert 'HTTP_ACCEPT_LANGUAGE: ru' in res, res
    assert "foo: 'baz'" in res, res


def test_post_extra_environ():
    app = webtest.TestApp(debug_app,
                          extra_environ={'HTTP_ACCEPT_LANGUAGE': 'ru',
                                         'foo': 'bar'})
    res = app.post('http://localhost/')
    assert 'HTTP_ACCEPT_LANGUAGE: ru' in res, res
    assert "foo: 'bar'" in res, res

    res = app.post('http://localhost/', extra_environ={'foo': 'baz'})
    assert 'HTTP_ACCEPT_LANGUAGE: ru' in res, res
    assert "foo: 'baz'" in res, res


def test_request_extra_environ():
    app = webtest.TestApp(debug_app,
                          extra_environ={'HTTP_ACCEPT_LANGUAGE': 'ru',
                                         'foo': 'bar'})
    res = app.request('http://localhost/', method='GET')
    assert 'HTTP_ACCEPT_LANGUAGE: ru' in res, res
    assert "foo: 'bar'" in res, res

    res = app.request('http://localhost/', method='GET', environ={'foo': 'baz'})
    assert 'HTTP_ACCEPT_LANGUAGE: ru' in res, res
    assert "foo: 'baz'" in res, res
