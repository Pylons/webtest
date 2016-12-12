=================================
Testing Applications with WebTest
=================================

:author: Ian Bicking <ianb@colorstudy.com>
:maintainer: Gael Pasgrimaud <gael@gawel.org>


Status & License
================

WebTest is an extraction of ``paste.fixture.TestApp``, rewriting
portions to use `WebOb <http://docs.webob.org/>`_.  It is under
active development as part of the Pylons cloud of packages.

Feedback and discussion should take place on the `Pylons discuss list
<https://groups.google.com/forum/?fromgroups#!forum/pylons-discuss>`_, and bugs
should go into the `Github tracker
<https://github.com/Pylons/webtest/issues>`_.

This library is licensed under an `MIT-style license <license.html>`_.

Installation
============

You can use pip or easy_install to get the latest stable release:

.. code-block:: sh

    $ pip install WebTest
    $ easy_install WebTest

Or if you want the development version:

.. code-block:: sh

    $ pip install https://nodeload.github.com/Pylons/webtest/tar.gz/master

What This Does
==============

WebTest helps you test your WSGI-based web applications.  This can be
any application that has a WSGI interface, including an application
written in a framework that supports WSGI (which includes most
actively developed Python web frameworks -- almost anything that even
nominally supports WSGI should be testable).

With this you can test your web applications without starting an HTTP
server, and without poking into the web framework shortcutting
pieces of your application that need to be tested.  The tests WebTest
runs are entirely equivalent to how a WSGI HTTP server would call an
application.  By testing the full stack of your application, the
WebTest testing model is sometimes called a *functional test*,
*integration test*, or *acceptance test* (though the latter two are
not particularly good descriptions).  This is in contrast to a *unit
test* which tests a particular piece of functionality in your
application.  While complex programming tasks are often suited to
unit tests, template logic and simple web programming is often best
done with functional tests; and regardless of the presence of unit
tests, no testing strategy is complete without high-level tests to
ensure the entire programming system works together.

WebTest helps you create tests by providing a convenient interface to
run WSGI applications and verify the output.

Quick start
===========

The most important object in WebTest is :class:`~webtest.app.TestApp`, the wrapper
for WSGI applications. It also allows you to perform HTTP requests on it.
To use it, you simply instantiate it with your WSGI application.

.. note::

   If your WSGI application requires any configuration,
   you must set that up manually in your tests.

Here is a basic application::

    >>> def application(environ, start_response):
    ...     headers = [('Content-Type', 'text/html; charset=utf8'),
    ...                ('Content-Length', str(len(body)))]
    ...     start_response('200 OK', headers)
    ...     return [body]

Wrap it into a :class:`~webtest.app.TestApp`::

    >>> from webtest import TestApp
    >>> app = TestApp(application)

Then you can get the response of a HTTP GET::

    >>> resp = app.get('/')

And check the results, like response's status::

    >>> assert resp.status == '200 OK'
    >>> assert resp.status_int == 200

Response's headers::

    >>> assert resp.content_type == 'text/html'
    >>> assert resp.content_length > 0

Or response's body::

    >>> resp.mustcontain('<html>')
    >>> assert 'form' in resp

WebTest can do much more. In particular, it can handle :doc:`forms`.


Contents
========


.. toctree::

   webtest.rst
   api.rst
   contributing.rst
   changelog.rst

.. include:: license.rst
