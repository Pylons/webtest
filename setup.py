from setuptools import setup, find_packages
import sys, os

version = '1.2.1'

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
        "Development Status :: 4 - Beta",
        "Framework :: Paste",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Server",
      ],
      keywords='wsgi test unit tests web',
      author='Ian Bicking',
      author_email='ianb@colorstudy.com',
      url='http://pythonpaste.org/webtest/',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
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
