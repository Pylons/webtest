News
====

2.0.25 (2017-02-05)
-------------------

- Fix #173: Do not omit file uploads without a file from post.
  [Michael Howitz]


2.0.24 (2016-12-16)
-------------------

- Drop python 2.6 support. Newer versions may still work if you use waitress < 1.0

- Remove bs4 warnings

- Docs improvments

- Tets are WebOb 1.7.x compatible


2.0.23 (2016-07-21)
-------------------

- Create universal wheels.


2.0.22 (2016-07-21)
-------------------

-  Fix #160: Do not guess encoding if response's charset is set.

2.0.21 (2016-04-12)
-------------------

- PR #154 Allow Bearer auth

- PR #147,#148 Take care of REFERER when using form.submit(), .click() and
  .clickbutton()

- PR #145 Allow to override content-type when using json methods

2.0.20 (2015-11-03)
-------------------

- nothing new release. just try to make wheel available on pypi


2.0.19 (2015-11-01)
-------------------

- fixed #131 prevent passing HTML parameters that conflict with Field kwargs

- fixed #135 Document that WSGIProxy2 is required for "using webtest with a real url"

- fixed #136 reset values of select multiple

- drop py32 support (still work but test dependencies fail)

2.0.18 (2015-02-05)
-------------------

- Avoid deprecation warning with py3.4


2.0.17 (2014-12-20)
-------------------

- Properly check for default cookiejar arguments
  [Julian Berman]

- Avoid raising encoding errors from debugapp (needed to use with WSGIProxy2)
  [Laurence Rowe]


2.0.16 (2014-09-19)
-------------------

- Fixed #110. Forced values for Radio inputs are no longer ignored by value
  property on get.
  [bayprogrammer]

- Added method TestApp.set_parser_features to change the parser_features used
  by BeautifulSoup.
  [tomasmoreyra]

- Added app.set_cookie
  [luhn]


2.0.15 (2014-04-17)
-------------------

- Fixed #73. Python < 2.6.5 does not support unicode as keyword arguments names.
  [Stepan Kolesnik]

- Fixed #84 Application cookies for localhost are no longer ignored
  [gawel]

- Fixed #89 remove WSGIWarning: You are not supposed to send a body in a DELETE
  request because we now have a good reason for that. See http://bit.ly/1tb3yxW
  [gawel]

- Fixed #92 You can now override TestApp.JSONEncoder to use a custom encoder
  [gawel]

- Fixed #93 Support basic authentication
  [gawel]

- Fixed #103 Broken "Edit me on GitHub" links in documentation
  [gawel]

- Fixed #106 Make wrapping the app in the lint middleware optional
  [dmlayton]

- Fixed #107 Explicit error message when WSGIProxy2 is not installer
  [gawel]

- Fixed #108 cgi.parse_qsl is pending deprecation
  [gawel]

2.0.14 (2014-01-23)
-------------------

- Allow `.select()` on <select>s and <select multiple>s.
  [Markus Bertheau]


2.0.13 (2014-01-23)
-------------------

- Allow selecting <select> options by text
  [Markus Bertheau]


2.0.12 (2014-01-17)
-------------------

- Ignore the `value` attribute of file inputs
  [Markus Bertheau]

- Allow selecting the form submit button by its value
  [Markus Bertheau]


2.0.11 (2013-12-29)
-------------------

- Depend on `unittest2` only for Python versions lower than 2.7
  [iElectric]

- Add an optional parameter to `TestApp`, allowing the user to specify the
  parser used by BeautifulSoup
  [lyndsysimon]


2.0.10 (2013-11-14)
-------------------

- Make StopableWSGIServer thread daemonic
  [lrowe]


2.0.9 (2013-09-18)
------------------

- Make sure Upload.content_type is not ignored
  https://github.com/Pylons/webtest/pull/88
  [Marius Gedminas]


2.0.8 (2013-09-17)
------------------

- Allow checking/unchecking a set of same-named checkboxes by assigning a list of values.
  [carljm]

- fix "AttributeError: 'InputWrapper' object has no attribute 'seek'"
  [iElectric]

- Added `xhr=True` parameter to `TestApp.get`, `TestApp.post`, `TestApp.head`, `TestApp.delete`
  [kharandziuk]

- Remove old (and broken?) casperjs/selenium backward compat imports. Fix
  https://github.com/gawel/webtest-selenium/issues/9
  [gawel]

- Allow optionally specifying the MIME type of an uploaded form file. Fixes #86
  [Marius Gedminas]


2.0.7 (2013-08-07)
------------------

- Detect JSON if mimetype ends with +json, such as application/vnd.webtest+json
  [homm]

- Fixed #72. Use WSGIServer new api even if there waitress has backward compat.
  [gawel]

- Fixed #50. Corrected default value for the delete params argument.
  [noonat]

- Be sure to decode the content if it is gziped before returning it
  [Alexis Métaireau]


2.0.6 (2013-05-23)
------------------

- fixed #64. cookiejar api has changed in python3.3 [gawel]

- allow to use a fixed StopableWSGIServer [gawel]

- Do not alter the BeautifulSoup object when parsing forms. [Georges
  Dubus]

- Remove first newline while parse textarea block, how modern browsers does.
  [Victor Safronovich] pull #69


2.0.5 (2013-04-12)
------------------

* Ignore select.error (not socket.error) following
  StopableWSGIServer.shutdown. [Laurence Rowe]

* Handle the short form of <select multiple> [Marius Gedminas]


2.0.4 (2013-03-28)
------------------

* Correctly handle <option> elements with no value attribute
  [Marius Gedminas]

* Ignore socket.error following StopableWSGIServer.shutdown. [Laurence Rowe]

* <button> without type='submit' attribute is treated as Submit
  control [Andrey Lebedev].

* Support for redirects having relative "Location" header [Andrey Lebedev]


2.0.3 (2013-03-19)
------------------

* Treat strings in the WSGI environment as native strings, compliant with
  PEP-3333. [wosc]


2.0.2 (2013-03-15)
------------------

* Allow TestResponse.click() to match HTML content again. [ender672]

* Support secure cookies [Andrey Lebedev]

2.0.1 (2013-03-05)
------------------

* Added Pasword field [diarmuidbourke]

* re-allow to use unknow field type. Like ``type="email"``. [gawel]

* Don't let BeautifulSoup use lxml. Fix GH-51 [kmike]

* added :meth:`webtest.response.TestResponse.maybe_follow` method [kmike]

2.0 (2013-02-25)
----------------

* drop zc.buildout usage for development, now using only virtualenv
  [Domen Kožar]

* Backward incompatibility : Removed the ``anchor`` argument of
  :meth:`webtest.response.TestResponse.click` and the ``button`` argument of
  :meth:`webtest.response.TestResponse.clickbutton`. It is for the greater good.
  [madjar]

* Rewrote API documentation [Domen Kožar]

* Added `wsgiproxy` support to do HTTP request to an URL [gawel]

* Use BeautifulSoup4 to parse forms [gawel]

* Added `webtest.app.TestApp.patch_json` [gawel]

* Implement `webtest.app.TestApp.cookiejar` support and kindof keep
  `webtest.app.TestApp.cookies` functionality.  `webtest.app.TestApp.cookies`
  should be treated as read-only.
  [Domen Kožar]

* Split Selenium integration into separate package webtest-selenium
  [gawel]

* Split casperjs integration into separate package webtest-casperjs
  [gawel]

* Test coverage improvements [harobed, cdevienne, arthru, Domen Kožar, gawel]

* Fully implement decoding of HTML entities

* Fix tox configuration

1.4.2
-----

* fix tests error due to CLRF in a tarball

1.4.1
-----

* add travis-ci

* migrate repository to https://github.com/Pylons/webtest

* Fix a typo in apps.py: selectedIndicies

* Preserve field order during parsing (support for deform and such)

* allow equals sign in the cookie by spliting name-value-string pairs on
  the first '=' sign as per
  http://tools.ietf.org/html/rfc6265#section-5.2

* fix an error when you use AssertionError(response) with unicode chars in
  response

1.4.0
-----

* added webtest.ext - allow to use casperjs

1.3.6
------

* fix `#42 <https://bitbucket.org/ianb/webtest/issue/42>`_ Check uppercase
  method.

* fix `#36 <https://bitbucket.org/ianb/webtest/issue/36>`_ Radio can use forced
  value.

* fix `#24 <https://bitbucket.org/ianb/webtest/issue/24>`_ Include test
  fixtures.

* fix bug when trying to print a response which contain some unicode chars

1.3.5
------

* fix `#39 <https://bitbucket.org/ianb/webtest/issue/39>`_ Add PATCH to
  acceptable methods.


1.3.4
-----

* fix `#33 <https://bitbucket.org/ianb/webtest/issue/33>`_ Remove
  CaptureStdout. Do nothing and break pdb

* use OrderedDict to store fields in form. See
  `#31 <https://bitbucket.org/ianb/webtest/issue/31>`_

* fix `#38 <https://bitbucket.org/ianb/webtest/issue/38>`_ Allow to post falsey
  values.

* fix `#37 <https://bitbucket.org/ianb/webtest/issue/37>`_ Allow
  Content-Length: 0 without Content-Type

* `fix #30 <https://bitbucket.org/ianb/webtest/issue/30>`_ bad link to pyquery
  documentation

* Never catch NameError during iteration

1.3.3
-----

* added ``post_json``, ``put_json``, ``delete_json``

* fix `#25 <https://bitbucket.org/ianb/webtest/issue/25>`_ params dictionary of
  webtest.AppTest.post() does not support unicode values

1.3.2
-----

* improve showbrowser. fixed `#23 <https://bitbucket.org/ianb/webtest/issue/23>`_

* print_stderr fail with unicode string on python2

1.3.1
-----

* Added .option() `#20 <https://bitbucket.org/ianb/webtest/issue/20>`_

* Fix #21

* Full python3 compat

1.3
---

* Moved TestApp to app.py

* Added selenium testing framework. See :mod:`~webtest.sel` module.


1.2.4
------

* Accept lists for ``app.post(url, params=[...])``

* Allow to use url that starts with the SCRIPT_NAME found in extra_environ

* Fix `#16 <https://bitbucket.org/ianb/webtest/issue/16>`_  Default
  content-type is now correctly set to `application/octet-stream`

* Fix `#14 and #18 <https://bitbucket.org/ianb/webtest/issue/18>`_ Allow to use
  `.delete(params={})`

* Fix `#12 <https://bitbucket.org/ianb/webtest/issue/12>`_ 


1.2.3
-----

* Fix `#10
  <http://bitbucket.org/ianb/webtest/issue/10/testapprequest-method-overwrites-specifics-with-testapp-scoped>`_,
  now `TestApp.extra_environ` doesn't take precedence over a WSGI
  environment passed in through the request.

* Removed stray print

1.2.2
-----

* Revert change to cookies that would add ``"`` around cookie values.

* Added property :meth:`webtest.Response.pyquery` which returns a
  `PyQuery <http://pyquery.org/>`_ object.

* Set base_url on ``resp.lxml``

* Include tests and docs in tarball.

* Fix sending in webob.Request (or webtest.TestRequest) objects.

* Fix handling forms with file uploads, when no file is selected.

* Added ``extra_environ`` argument to :meth:`webtest.TestResponse.click`.

* Fixed/added wildcard statuses, like ``status="4*"``

* Fix file upload fields in forms: allow upload field to be empty.

* Added support for single-quoted html attributes.

* `TestResponse` now has unicode support. It is turned on by default
  for all responses with charset information. **This is backward
  incompatible change** if you rely (e.g. in doctests) on parsed
  form fields or responses returned by `json` and `lxml` methods
  being encoded strings when charset header is in response. In order
  to switch to old behaviour pass `use_unicode=False` flag to
  `TestApp` constructor.


1.2.1
-----

* Added method :meth:`TestApp.request`, which can be used for
  sending requests with different methods (e.g., ``MKCOL``).  This
  method sends all its keyword arguments to
  :meth:`webtest.TestRequest.blank` and then executes the request.
  The parameters are somewhat different than other methods (like
  :meth:`webtest.TestApp.get`), as they match WebOb's attribute
  names exactly (the other methods were written before WebOb existed).

* Removed the copying of stdout to stderr during requests.

* Fix file upload fields in forms (`#340
  <http://trac.pythonpaste.org/pythonpaste/ticket/340>`_) -- you could
  upload files with :meth:`webtest.TestApp.post`, but if you use
  ``resp.form`` file upload fields would not work (from rcs-comp.com
  and Matthew Desmarais).

1.2
---

* Fix form inputs; text inputs always default to the empty string, and
  unselected radio inputs default to nothing at all.  From Daniele
  Paolella.

* Fix following links with fragments (these fragments should not be
  sent to the WSGI application).  From desmaj.

* Added ``force_value`` to select fields, like
  ``res.form['select'].force_value("new_value")``.  This makes it
  possible to simulate forms that are dynamically updated.  From
  Matthew Desmarais.

* Fixed :meth:`webtest.Response.mustcontain` when you pass in a
  ``no=[strings]`` argument.

1.1
---

* Changed the ``__str__`` of responses to make them more doctest
  friendly:

  - All headers are displayed capitalized, like Content-Type
  - Headers are sorted alphabetically

* Changed ``__repr__`` to only show the body length if the complete
  body is not shown (for short bodies the complete body is in the
  repr)

* Note: **these are backward incompatible changes** if you are using
  doctest (you'll have to update your doctests with the new format).

* Fixed exception in the ``.delete`` method.

* Added a ``content_type`` argument to ``app.post`` and ``app.put``,
  which sets the ``Content-Type`` of the request.  This is more
  convenient when testing REST APIs.

* Skip links in ``<script>...</script>`` tags (since that's not real
  markup).

1.0.2
-----

* Don't submit unnamed form fields.

* Checkboxes with no explicit ``value`` send ``on`` (previously they
  sent ``checked``, which isn't what browsers send).

* Support for ``<select multiple>`` fields (from Matthew Desmarais)

1.0.1
---

* Fix the ``TestApp`` validator's InputWrapper lacking support for
  readline with an argument as needed by the cgi module.

1.0
---

* Keep URLs in-tact in cases such as
  ``app.get('http://www.python.org')`` (so HTTP_HOST=www.python.org,
  etc).

* Fix ``lxml.html`` import, so lxml 2.0 users can get HTML lxml
  objects from ``resp.lxml``

* Treat ``<input type="image">`` like a submit button.

* Use ``BaseCookie`` instead of ``SimpleCookie`` for storing cookies
  (avoids quoting cookie values).

* Accept any ``params`` argument that has an ``items`` method (like
  MultiDict)

0.9
---

Initial release
