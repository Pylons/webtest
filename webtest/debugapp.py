from webob import Request
try:
    sorted
except NameError:
    from webtest import sorted

__all__ = ['debug_app']

def debug_app(environ, start_response):
    req = Request(environ)
    if 'error' in req.GET:
        raise Exception('Exception requested')
    status = req.GET.get('status', '200 OK')
    parts = []
    for name, value in sorted(environ.items()):
        if name.upper() != name:
            value = repr(value)
        parts.append('%s: %s\n' % (name, value))
    req_body = req.body
    if req_body:
        parts.append('-- Body ----------\n')
        parts.append(req_body)
    body = ''.join(parts)
    headers = [
        ('Content-Type', 'text/plain'),
        ('Content-Length', str(len(body)))]
    for name, value in req.GET.items():
        if name.startswith('header-'):
            header_name = name[len('header-'):]
            headers.append((header_name, value))
    start_response(status, headers)
    return [body]

def make_debug_app(global_conf):
    """
    An application that displays the request environment, and does
    nothing else (useful for debugging and test purposes).
    """
    return debug_app
