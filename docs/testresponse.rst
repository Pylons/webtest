TestResponse
############

..
  >>> import json
  >>> import sys
  >>> from webob import Request
  >>> from webob import Response
  >>> from webtest.app import TestApp
  >>> def application(environ, start_response):
  ...     req = Request(environ)
  ...     if req.path_info.endswith('.html'):
  ...         content_type = 'text/html'
  ...         body = '<html><body><div id="content">hey!</div></body>'.encode('latin-1')
  ...     elif req.path_info.endswith('.xml'):
  ...         content_type = 'text/xml'
  ...         body = '<xml><message>hey!</message></xml>'.encode('latin-1')
  ...     elif req.path_info.endswith('.json'):
  ...         content_type = 'application/json'
  ...         body = json.dumps({"a": 1, "b": 2}).encode('latin-1')
  ...     resp = Response(body, content_type=content_type)
  ...     return resp(environ, start_response)
  >>> app = TestApp(application)


The response object is based on :class:`webob.response.Response` with some additions
to help with testing.

The inherited attributes that are most interesting:

``response.status``:
    The text status of the response, e.g., ``"200 OK"``.

``response.status_int``:
    The text status_int of the response, e.g., ``200``.

``response.headers``:
    A dictionary-like object of the headers in the response.

``response.body``:
    The text body of the response.

``response.text``:
    The unicode text body of the response.

``response.normal_body``:
    The whitespace-normalized [#whitespace-normalized]_ body of the response.

``response.request``:
    The :class:`webob.request.BaseRequest` object used to generate
    this response.

The added methods:

``response.follow(**kw)``:
    Follows the redirect, returning the new response.  It is an error
    if this response wasn't a redirect. All keyword arguments are
    passed to :class:`webtest.app.TestApp` (e.g., ``status``). Returns
    another response object.

``response.maybe_follow(**kw)``:
    Follows all redirects; does nothing if this response
    is not a redirect. All keyword arguments are passed
    to :class:`webtest.app.TestApp` (e.g., ``status``). Returns another
    response object.

``x in response``:
    Returns True if the string is found in the response body.
    Whitespace is normalized for this test.

``response.mustcontain(string1, string2, no=string3)``:
    Raises an error if any of the strings are not found in the
    response.  If a string of a string list is given as `no` keyword
    argument, raise an error if one of those are found in the
    response.  It also prints out the response in that case, so you
    can see the real response.

``response.showbrowser()``:
    Opens the HTML response in a browser; useful for debugging.

``str(response)``:
    Gives a slightly-compacted version of the response.  This is
    compacted to remove newlines, making it easier to use with
    :mod:`python:doctest`.

``response.click(description=None, linkid=None, href=None, anchor=None, index=None, verbose=False)``:
    Clicks the described link (see :meth:`~webtest.response.TestResponse.click`)

``response.forms``:
    Return a dictionary of forms; you can use both indexes (refer to
    the forms in order) or the string ids of forms (if you've given
    them ids) to identify the form. See :doc:`forms` for more on the form
    objects.

``response.form``:
    If there is just a single form, this returns that.  It is an error
    if you use this and there are multiple forms.


.. rubric:: Footnotes

.. [#whitespace-normalized] The whitespace normalization replace sequences of whitespace characters and ``\n`` ``\r`` ``\t`` by a single space.


.. toctree::

    forms.rst


Parsing the Body
================

There are several ways to get parsed versions of the response.  These
are the attributes:

``response.html``:
    Return a `BeautifulSoup
    <https://www.crummy.com/software/BeautifulSoup/>`_ version of the
    response body::

        >>> res = app.get('/index.html')
        >>> res.html
        <html><body><div id="content">hey!</div></body></html>
        >>> res.html.__class__
        <class '...BeautifulSoup'>

``response.xml``:
    Return an :mod:`ElementTree <python:xml.etree.ElementTree>`
    version of the response body::

        >>> res = app.get('/document.xml')
        >>> res.xml
        <Element 'xml' ...>
        >>> res.xml[0].tag
        'message'
        >>> res.xml[0].text
        'hey!'


``response.lxml``:
    Return an `lxml <https://lxml.de/>`_ version of the response body::

        >>> res = app.get('/index.html')
        >>> res.lxml
        <Element html at ...>
        >>> res.lxml.xpath('//body/div')[0].text
        'hey!'

        >>> res = app.get('/document.xml')
        >>> res.lxml
        <Element xml at ...>
        >>> res.lxml[0].tag
        'message'
        >>> res.lxml[0].text
        'hey!'

``response.pyquery``:
    Return a `PyQuery <https://pypi.org/project/pyquery/>`_ version of the
    response body::

        >>> res.pyquery('message')
        [<message>]
        >>> res.pyquery('message').text()
        'hey!'

``response.json``:
    Return the parsed JSON (parsed with `simplejson
    <http://svn.red-bean.com/bob/simplejson/tags/simplejson-1.7/docs/index.html>`_)::

        >>> res = app.get('/object.json')
        >>> sorted(res.json.values())
        [1, 2]


In each case the content-type must be correct or an AttributeError is
raised.  If you do not have the necessary library installed (none of
them are required by WebTest), you will get an ImportError.
