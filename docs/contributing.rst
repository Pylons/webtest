=============================
Contribute to webtest project
=============================

Getting started
===============

Get your working copy :

.. code-block:: bash

    $ git clone https://github.com/Pylons/webtest.git
    $ cd webtest
    $ uv sync

Now, you can hack.


Execute tests
=============

.. code-block:: bash

    $ uv run pytest
    ============================= test session starts ==============================
    platform linux -- Python 3.14.0, pytest-9.0.2, pluggy-1.6.0
    rootdir: /home/user/webtest
    configfile: pyproject.toml
    plugins: cov-7.0.0
    collected 206 items

    tests/test_app.py ............................................           [ 21%]
    tests/test_authorisation.py ...                                          [ 22%]
    tests/test_debugapp.py ......................                            [ 33%]
    tests/test_ext.py .                                                      [ 33%]
    tests/test_forms.py .................................................... [ 59%]
    .                                                                        [ 59%]
    tests/test_http.py ....                                                  [ 61%]
    tests/test_lint.py ............................                          [ 75%]
    tests/test_response.py ...............................                   [ 90%]
    tests/test_sel.py .                                                      [ 90%]
    tests/test_utils.py ..................                                   [ 99%]
    webtest/forms.py .                                                       [100%]

    ============================= 206 passed in 3.81s ==============================


Use tox to test many Python versions
====================================

.. code-block:: bash

    $ uvx --with tox-uv tox
    py39: commands succeeded
    py310: commands succeeded
    py311: commands succeeded
    py312: commands succeeded

To execute tests on all Python versions, you need to have ``python3.9``, ``python3.10``, ``python3.11`` and ``python3.12`` in your ``PATH``.


Generate documentation
======================

.. code-block:: bash

    $ cd docs
    $ make html
    ...
    build succeeded.

    Build finished. The HTML pages are in _build/html.


Tips
====

You can use :doc:`debugapp` object to test *webtest*.
