# (c) 2005 Ian Bicking and contributors; written for Paste (http://pythonpaste.org)
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
"""
Routines for testing WSGI applications.

Most interesting is TestApp
"""

from webtest.testapp import TestApp
from webtest.testapp import TestRequest
from webtest.testapp import TestResponse
from webtest.testapp import Form
from webtest.testapp import Field
from webtest.testapp import AppError
from webtest.testapp import Select
from webtest.testapp import Radio
from webtest.testapp import Checkbox
from webtest.testapp import Text
from webtest.testapp import Textarea
from webtest.testapp import Hidden
from webtest.testapp import Submit

