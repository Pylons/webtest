# -*- coding: utf-8 -*-
import doctest
import os


def setup_test(test):
    fd = open(os.path.join(os.path.dirname(__file__), 'form.html'), 'rb')
    body = fd.read()
    fd.close()
    test.globs.update(body=body)
    for example in test.examples:
        example.options.setdefault(doctest.ELLIPSIS, 1)
        example.options.setdefault(doctest.NORMALIZE_WHITESPACE, 1)

setup_test.__test__ = False
