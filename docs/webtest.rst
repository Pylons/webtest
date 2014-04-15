======================================
Functional Testing of Web Applications
======================================


.. toctree::

   testapp.rst
   testresponse.rst
   http.rst
   debugapp.rst


Framework Hooks
===============

Frameworks can detect that they are in a testing environment by the
presence (and truth) of the WSGI environmental variable
``"paste.testing"`` (the key name is inherited from
``paste.fixture``).

More generally, frameworks can detect that something (possibly a test
fixture) is ready to catch unexpected errors by the presence and truth
of ``"paste.throw_errors"`` (this is sometimes set outside of testing
fixtures too, when an error-handling middleware is in place).

Frameworks that want to expose the inner structure of the request may
use ``"paste.testing_variables"``.  This will be a dictionary -- any
values put into that dictionary will become attributes of the response
object.  So if you do ``env["paste.testing_variables"]['template'] =
template_name`` in your framework, then ``response.template`` will be
``template_name``.
