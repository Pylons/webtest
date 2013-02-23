======================
WSGI Debug application
======================

``webtest.debugapp.debug_app`` is a faker WSGI app to help to test *webtest*.

Examples of use :

.. code-block:: python

    >>> import webtest
    >>> from webtest.debugapp import debug_app
    >>> app = webtest.TestApp(debug_app)
    >>> res = app.post('/', params='foobar')
    >>> print(res.body) # doctest: +SKIP
    CONTENT_LENGTH: 6
    CONTENT_TYPE: application/x-www-form-urlencoded
    HTTP_HOST: localhost:80
    ...
    wsgi.url_scheme: 'http'
    wsgi.version: (1, 0)
    -- Body ----------
    foobar

Here, you can see, ``foobar`` in *body* when you pass ``foobar`` in ``app.post`` ``params`` argument.

You can also define the status of response :

    >>> res = app.post('/?status=302', params='foobar')
    >>> print(res.status)
    302 Found
