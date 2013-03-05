#!/usr/bin/env python
# vim: set et fileencoding=utf8 sts=4 sw=4 ts=4
"""
    ch03.tests.bytecode
    ~~~~~~~~~~~~~~~~~~~

    Specifies the behavior of the bytecode module.

    :copyright: 2013 by Austin Hastings, see AUTHORS for more details.
    :license: GPL v3+, see LICENSE for more details.
"""
from io import StringIO
import pdb
import sys
import unittest

from ch03.bytecode import CodeObject

class TestBytecode(unittest.TestCase):

    def test_return42(self):
        co = CodeObject()
        co.append('LOAD_CONST', 42)
        co.append('RETURN_VALUE')
        expected = """
            LOAD_CONST      1 (42)
            RETURN_VALUE
       """
        co.check_bytecode(expected)

if __name__ == '__main__':
    unittest.main()
