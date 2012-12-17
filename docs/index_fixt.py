# -*- coding: utf-8 -*-
import doctest


def setup_test(test):
    for example in test.examples:
        example.options.setdefault(doctest.ELLIPSIS, 1)
        example.options.setdefault(doctest.NORMALIZE_WHITESPACE, 1)

setup_test.__test__ = False
