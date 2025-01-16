#!/usr/bin/env python

from setuptools import setup
from setuptools import find_packages

version = '3.0.3'

install_requires = [
    'WebOb>=1.2',
    'waitress>=3.0.2',
    'beautifulsoup4',
]

tests_require = [
    'coverage',
    'PasteDeploy',
    'pyquery',
    'pytest',
    'pytest-cov',
    'WSGIProxy2',
]

docs_extras = [
    'docutils',
    'pylons-sphinx-themes >= 1.0.8',
    'Sphinx >= 3.0.0',
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
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3 :: Only",
          "Programming Language :: Python :: 3.9",
          "Programming Language :: Python :: 3.10",
          "Programming Language :: Python :: 3.11",
          "Programming Language :: Python :: 3.12",
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
      python_requires='>=3.9',
      install_requires=install_requires,
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
