# -*- coding: utf-8 -*-
from doctest import ELLIPSIS


def setup_test(test):
    raise ValueError(test.globs)
    for example in test.examples:
        example.options.setdefault(ELLIPSIS, 1)

setup_test.__test__ = False
