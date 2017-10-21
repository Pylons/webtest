Releasing WebTest
=================

- For clarity, we define releases as follows.

  - Alpha, beta, dev and similar statuses do not qualify whether a release is
    major or minor. The term "pre-release" means alpha, beta, or dev.

  - A release is final when it is no longer pre-release.

  - A *major* release is where the first number either before or after the
    first dot increases. Examples: 1.6 to 1.7a1, or 1.8 to 2.0.

  - A *minor* or *bug fix* release is where the number after the second dot
    increases. Example: 1.6 to 1.6.1.


Releasing with zest.releaser
----------------------------

- First install `zest.releaser <https://pypi.python.org/pypi/zest.releaser>`_::

    $ pip install zest.releaser[recommanded]

- Add this to your ``~/.pypirc``::

    [zest.releaser]
    no-input = true
    create-wheel = yes

- Edit ``CHANGELOG.rst``

- Run the fullrelease script::

    $ fullrelease

Marketing and communications
----------------------------

- Announce to Twitter::

    WebTest 2.0.x released.

    PyPI
    https://pypi.python.org/pypi/webtest/2.0.x

    Changes
    https://docs.pylonsproject.org/projects/webtest/en/latest/changelog.html

    Issues
    https://github.com/Pylons/webtest/issues

- Announce to maillist::

    WebTest 2.0.x has been released.

    Here are the changes:

    <<changes>>

    You can install it via PyPI:

      pip install WebTest==2.0.x

    Enjoy, and please report any issues you find to the issue tracker at
    https://github.com/Pylons/webtest/issues

    Thanks!

    - WebTest developers

Here is a command line to get those text without indent and version replaced::

    cat RELEASING.rst | sed 's/2.0.x/version/' | sed 's/    //'
