import unittest
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

class TestTesting(unittest.TestCase):

    def setUp(self):
        self.app = webtest.TestApp(debug_app)

    def test_testing(self):
        res = self.app.get('/')
        assert res.status_int == 200
        assert res.headers['content-type'] == 'text/plain'
        assert res.content_type == 'text/plain'
        res = self.app.request('/', method='GET')
        assert res.status_int == 200
        assert res.headers['content-type'] == 'text/plain'
        assert res.content_type == 'text/plain'
        res = self.app.head('/')
        assert res.status_int == 200
        assert res.headers['content-type'] == 'text/plain'
        assert res.content_length
        assert res.body == ''

    def test_get_params(self):
        res = self.app.post('/', params=dict(a=1))
        res.mustcontain('a=1')
        res = self.app.post('/', params=[('a','1')])
        res.mustcontain('a=1')

    def test_delete_params(self):
        res = self.app.delete('/', params=dict(a=1))
        res.mustcontain('a=1')

    def test_exception(self):
        raises(Exception, self.app.get, '/?error=t')
        raises(webtest.AppError, self.app.get, '/?status=404%20Not%20Found')

    def test_303(self):
        res = self.app.get('/?status=303%20Redirect&header-location=/foo')
        assert res.status_int == 303
        print res.location
        assert res.location == '/foo'
        assert res.headers['location'] == '/foo'
        res = res.follow()
        assert res.request.url == 'http://localhost/foo'
        assert 'Response: 200 OK' in str(res)
        assert '200 OK' in repr(res)
        res = self.app.get('/?status=303%20redirect', status='3*')

    def test_204(self):
        res = self.app.post('/?status=204%20OK')

    def test_404(self):
        self.app.get('/?status=404%20Not%20Found', status=404)
        raises(webtest.AppError, self.app.get, '/', status=404)

    def test_fake_dict(self):
        class FakeDict(object):
            def items(self):
                return [('a', '10'), ('a', '20')]
        res = self.app.post('/params', params=FakeDict())

