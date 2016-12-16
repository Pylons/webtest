# -*- coding: utf-8 -*-

import unittest  # noqa

try:
    unicode()
except NameError:
    b = bytes

    def u(value):
        if isinstance(value, bytes):
            return value.decode('utf-8')
        return value
else:
    def b(value):
        return str(value)

    def u(value):
        if isinstance(value, unicode):
            return value
        return unicode(value, 'utf-8')
