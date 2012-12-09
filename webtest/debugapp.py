import webob
import six


__all__ = ['debug_app']


def debug_app(environ, start_response):
    """The WSGI application used for testing"""
    req = webob.Request(environ)
    if req.path_info == '/form.html' and req.method == 'GET':
        resp = webob.Response(content_type='text/html')
        resp.body = six.b('''<html><body>
        <form action="/form-submit" method="POST">
            <input type="text" name="name">
            <input type="submit" name="submit" value="Submit!">
        </form></body></html>''')
        return resp(environ, start_response)

    if 'error' in req.GET:
        raise Exception('Exception requested')
    status = str(req.GET.get('status', '200 OK'))

    parts = []
    for name, value in sorted(environ.items()):
        if name.upper() != name:
            value = repr(value)
        parts.append(str('%s: %s\n') % (name, value))

    body = ''.join(parts)
    if not isinstance(body, six.binary_type):
        body = body.encode('ascii')

    if req.content_length:
        body += six.b('-- Body ----------\n')
        body += req.body

    if status[:3] in ('204', '304') and not req.content_length:
        body = ''

    headers = [
        ('Content-Type', str('text/plain')),
        ('Content-Length', str(len(body)))]

    for name, value in req.GET.items():
        if name.startswith('header-'):
            header_name = name[len('header-'):]
            headers.append((header_name, str(value)))

    resp = webob.Response()
    resp.status = status
    resp.headers.update(headers)
    if req.method != 'HEAD':
        if isinstance(body, six.text_type):
            resp.body = body.encode('utf8')
        else:
            resp.body = body
    return resp(environ, start_response)


def make_debug_app(global_conf):
    """An application that displays the request environment, and does
    nothing else (useful for debugging and test purposes).
    """
    return debug_app
