TestApp
=======

Making Requests
---------------

To make a request, use:

.. code-block:: python

    app.get('/path', [params], [headers], [extra_environ], ...)

This call to :meth:`~webtest.app.TestApp.get` does a request for
``/path``, with any params, extra headers or WSGI
environment keys that you indicate.  This returns a
:class:`~webtest.response.TestResponse` object,
based on :class:`webob.response.Response`.  It has some
additional methods to make it easier to test.

If you want to do a POST request, use:

.. code-block:: python

    app.post('/path', {'vars': 'values'}, [headers], [extra_environ],
             [upload_files], ...)

Specifically the second argument of :meth:`~webtest.app.TestApp.post`
is the *body* of the request.  You
can pass in a dictionary (or dictionary-like object), or a string
body (dictionary objects are turned into HTML form submissions).

You can also pass in the keyword argument upload_files, which is a
list of ``[(fieldname, filename, field_content)]``.  File uploads use a
different form submission data type to pass the structured data.

You can use :meth:`~webtest.app.TestApp.put` and
:meth:`~webtest.app.TestApp.delete` for PUT and DELETE requests.


Making JSON Requests
--------------------

Webtest provide some facilities to test json apis.

The ``*_json`` methods will transform data to json before ``POST``/``PUT`` and
add the correct ``Content-Type`` for you.

Also Response have an attribute :attr:`~webtest.response.TestResponse.json` to allow you to retrieve json
contents as a python dict.

Doing *POST* request with :meth:`webtest.app.TestApp.post_json`:

.. code-block:: python

    >>> resp = app.post_json('/resource/', dict(id=1, value='value'))
    >>> print(resp.request)
    POST /resource/ HTTP/1.0
    Content-Length: 27
    Content-Type: application/json
    ...

    >>> resp.json == {'id': 1, 'value': 'value'}
    True


Doing *GET* request with :meth:`webtest.app.TestApp.get` and using :attr:`~webtest.response.TestResponse.json`:

To just parse body of the response, use Response.json:

.. code-block:: python

    >>> resp = app.get('/resource/1/')
    >>> print(resp.request)
    GET /resource/1/ HTTP/1.0
    ...

    >>> resp.json == {'id': 1, 'value': 'value'}
    True



Modifying the Environment & Simulating Authentication
------------------------------------------------------

The best way to simulate authentication is if your application looks
in ``environ['REMOTE_USER']`` to see if someone is authenticated.
Then you can simply set that value, like:

.. code-block:: python

    app.get('/secret', extra_environ=dict(REMOTE_USER='bob'))

If you want *all* your requests to have this key, do:

.. code-block:: python

    app = TestApp(my_app, extra_environ=dict(REMOTE_USER='bob'))

If you have to use HTTP authorization you can use the ``.authorization``
property to set the ``HTTP_AUTHORIZATION`` key of the extra_environ
dictionnary:

.. code-block:: python

    app = TestApp(my_app)
    app.authorization = ('Basic', ('user', 'password'))

Only Basic auth is supported for now.

Testing a non wsgi application
------------------------------

You can use WebTest to test an application on a real web server.
Just pass an url to the `TestApp` instead of a WSGI application::

    app = TestApp('http://my.cool.websi.te')

You can also use the ``WEBTEST_TARGET_URL`` env var to switch from a WSGI
application to a real server without having to modify your code::

    os.environ['WEBTEST_TARGET_URL'] = 'http://my.cool.websi.te'
    app = TestApp(wsgiapp) # will use the WEBTEST_TARGET_URL instead of the wsgiapp

By default the proxy will use ``httplib`` but you can use other backends by
adding an anchor to your url::

    app = TestApp('http://my.cool.websi.te#urllib3')
    app = TestApp('http://my.cool.websi.te#requests')
    app = TestApp('http://my.cool.websi.te#restkit')

What Is Tested By Default
--------------------------

A key concept behind WebTest is that there's lots of things you
shouldn't have to check everytime you do a request.  It is assumed
that the response will either be a 2xx or 3xx response; if it isn't an
exception will be raised (you can override this for a request, of
course).  The WSGI application is tested for WSGI compliance with
a slightly modified version of `wsgiref.validate
<http://python.org/doc/current/lib/module-wsgiref.validate.html>`_
(modified to support arguments to ``InputWrapper.readline``)
automatically.  Also it checks that nothing is printed to the
``environ['wsgi.errors']`` error stream, which typically indicates a
problem (one that would be non-fatal in a production situation, but if
you are testing is something you should avoid).

To indicate another status is expected, use the keyword argument
``status=404`` to (for example) check that it is a 404 status, or
``status="*"`` to allow any status, or ``status="400 Custom Bad Request"``
to use custom reason phrase.

If you expect errors to be printed, use ``expect_errors=True``.
