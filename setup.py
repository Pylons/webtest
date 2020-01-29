#!/usr/bin/env python

from setuptools import setup
from setuptools import find_packages

version = '2.0.34'

install_requires = [
    'six',
    'WebOb>=1.2',
    'waitress>=0.8.5',
    'beautifulsoup4',
]

tests_require = [
    'nose<1.3.0', 'coverage', 'mock',
    'PasteDeploy', 'WSGIProxy2', 'pyquery'
]

docs_extras = [
    'Sphinx >= 1.8.1',
    'docutils',
    'pylons-sphinx-themes >= 1.0.8',
]

setup(name='WebTest',
      version=version,
      description="Helper to test WSGI applications",
      long_description=open('README.rst').read(),
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Framework :: Paste",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Topic :: Internet :: WWW/HTTP :: WSGI",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Server",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
      ],
      keywords='wsgi test unit tests web',
      author='Ian Bicking',
      maintainer='Gael Pasgrimaud',
      maintainer_email='gael@gawel.org',
      url='https://docs.pylonsproject.org/projects/webtest/en/latest/',
      license='MIT',
      packages=find_packages(exclude=[
          'ez_setup',
          'examples',
          'tests',
          'bootstrap',
          'bootstrap-py3k',
      ]),
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      test_suite='nose.collector',
      tests_require=tests_require,
      extras_require={
          'tests': tests_require,
          'docs': docs_extras,
      },
      entry_points="""
      [paste.app_factory]
      debug = webtest.debugapp:make_debug_app
      """,
      )
