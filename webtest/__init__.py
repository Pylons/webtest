# (c) 2005 Ian Bicking and contributors; written for Paste
# (http://pythonpaste.org)
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php
"""
Routines for testing WSGI applications.
"""

from webtest.app import TestApp
from webtest.app import TestRequest
from webtest.app import TestResponse
from webtest.app import AppError
from webtest.forms import Form
from webtest.forms import Field
from webtest.forms import Select
from webtest.forms import Radio
from webtest.forms import Checkbox
from webtest.forms import Text
from webtest.forms import Textarea
from webtest.forms import Hidden
from webtest.forms import Submit
from webtest.forms import Upload

# backward compat
try:
    import webtest_casperjs
except ImportError:
    from webtest.ext import casperjs
else:  # pragma: no cover
    from webtest_casperjs import casperjs
try:
    import webtest_selenium
except ImportError:
    from webtest.sel import SeleniumApp
    from webtest.sel import selenium
else:  # pragma: no cover
    from webtest_selenium import SeleniumApp
    from webtest_selenium import selenium
