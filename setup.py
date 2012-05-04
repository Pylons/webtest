#!/usr/bin/env python
from setuptools import setup
from setuptools import find_packages

version = '1.3.4'

setup(name='WebTest',
      version=version,
      description="Helper to test WSGI applications",
      long_description="""\
This wraps any WSGI application and makes it easy to send test
requests to that application, without starting up an HTTP server.

This provides convenient full-stack testing of applications written
with any WSGI-compatible framework.

This is based on ``paste.fixture.TestApp``.
""",
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Paste",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Server",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
      ],
      keywords='wsgi test unit tests web',
      author='Ian Bicking',
      author_email='ianb at colorstudy com',
      maintainer='Gael Pasgrimaud',
      maintainer_email='gael@gawel.org',
      url='http://webtest.pythonpaste.org/',
      license='MIT',
      packages=find_packages(exclude=[
          'ez_setup', 'examples', 'tests',
          'bootstrap', 'bootstrap-py3k',
      ]),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'WebOb',
      ],
      test_suite='nose.collector',
      tests_require=['dtopt', 'nose'],
      entry_points="""
      [paste.app_factory]
      debug = webtest.debugapp:make_debug_app
      """,
      )
