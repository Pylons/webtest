=============================
Contribute to webtest project
=============================

Getting started
===============

Get your working copy :

.. code-block:: bash

    $ git clone https://github.com/Pylons/webtest.git
    $ cd webtest
    $ virtualenv .
    $ . bin/activate
    $ python setup.py dev

Now, you can hack.


Execute tests
=============

.. code-block:: bash

    $ bin/nosetests
    Doctest: forms.rst ... ok
    Doctest: index.rst ... ok

    ...

    test_url_class (tests.test_testing.TestTesting) ... ok
    tests.test_testing.test_print_unicode ... °C
    ok

    Name               Stmts   Miss  Cover   Missing
    ------------------------------------------------
    webtest               18      0   100%   
    webtest.app          603     92    85%   48, 61-62, 94, 98, 212-221, 264-265, 268-272, 347, 379-386, 422, 426-428, 432-434, 455, 463, 471, 473, 488, 496-497, 515, 520-527, 548, 553-554, 558-559, 577, 592, 597-598, 618, 624, 661-664, 742, 808, 872, 940-941, 945-948, 961-964, 975, 982, 995, 1000, 1006, 1010, 1049, 1051, 1095-1096, 1118-1119, 1122-1127, 1135-1136, 1148, 1155-1160, 1175
    webtest.compat        50     11    78%   28-34, 55-56, 61-62
    webtest.debugapp      58      0   100%   
    webtest.ext           80      0   100%   
    webtest.forms        324     23    93%   23, 49, 58, 61, 92, 116, 177, 205, 411, 478, 482-486, 491-493, 522, 538, 558-561
    webtest.http          78      0   100%   
    webtest.lint         215     45    79%   135, 176, 214-216, 219-224, 227-231, 234, 243-244, 247, 250-251, 254, 263-264, 270, 274, 307, 311, 335, 359, 407, 424-427, 441-444, 476-479, 493, 508
    webtest.sel          479    318    34%   38-39, 45-46, 64-78, 88-108, 120, 126, 151-153, 156-158, 164-165, 168-191, 194-201, 219-231, 236, 240, 243-259, 263-297, 301-306, 316-326, 331-336, 340, 344, 347-352, 357-359, 364, 392-394, 397-404, 408, 412-417, 421, 425-426, 430, 434, 438, 442, 445, 448-457, 470-480, 483-485, 488, 492, 495, 503, 506, 515-516, 520, 524, 528, 533, 538, 542-544, 547, 560-565, 576, 579, 582, 593-596, 599-602, 605-606, 617-620, 623-642, 668-677, 680-688, 715, 720, 732, 735, 744-754, 757-762, 770-779, 791, 794, 805-809, 813-826, 838-842
    webtest.utils         99     11    89%   19-20, 23, 26, 32, 38, 100, 109, 152-154
    ------------------------------------------------
    TOTAL               2004    500    75%   
    ----------------------------------------------------------------------
    Ran 70 tests in 14.940s


Use tox to test many Python versions
====================================

`Tox <http://tox.testrun.org/>`_ installation :

.. code-block:: bash

    $ pip install tox
    $ tox

Launch tests with *tox* :

.. code-block:: bash

    $ bin/tox
    py26: commands succeeded
    py27: commands succeeded
    py32: commands succeeded
    py33: commands succeeded

To execute test on all python versions, you need to have ``python2.6``, ``python2.7``, ``python3.2`` and ``python3.3`` in your ``PATH``.


Generate documentation
======================

.. code-block:: bash

    $ pip install Sphinx
    $ cd docs
    $ make html
    ../bin/sphinx-build -b html -d _build/doctrees   . _build/html
    Running Sphinx v1.1.3
    loading pickled environment... done

    ...

    build succeeded, 3 warnings.

    Build finished. The HTML pages are in _build/html.


Tips
====

You can use :doc:`debugapp` object to test *webtest*.
