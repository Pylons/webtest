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

