# -*- coding: utf-8 -*-
try:
    # py < 2.7
    import unnitest2 as unittest
except ImportError:
    import unittest

try:
    unicode()
except NameError:
    u = str
else:
    def u(value):
        return unicode(value, 'utf-8')

def raises(exc, func, *args, **kw):
    try:
        func(*args, **kw)
    except exc:
        pass
    else:
        raise AssertionError(
            "Expected exception %s from %s"
            % (exc, func))

