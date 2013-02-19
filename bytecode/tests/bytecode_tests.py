#!/usr/bin/env python
# vim: set et fileencoding=utf8 sts=4 sw=4 ts=4
"""
    bytecode.tests.bytecode_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Specifies the behavior of the bytecode module.

    :copyright: 2013 by Austin Hastings, see AUTHORS for more details.
    :license: GPL v3+, see LICENSE for more details.
"""
from io import StringIO
import pdb
import sys
import unittest

from bytecode import CodeObject

class TestBytecode(unittest.TestCase):

    def test_append(self):
        """
        Test that our opcodes are emitted correctly using some known-good
        data generated by Python.
        """
        co = CodeObject()
        co.append('LOAD_CONST', 42)
        co.append('RETURN_VALUE')
        expected = bytearray(b"d\x01\x00S")
        self.assertEqual(len(expected), 4)
        self.assertEqual(co.co_code, expected)

    def test_return42(self):
        co = CodeObject()
        co.append('LOAD_CONST', 42)
        co.append('RETURN_VALUE')
        asm = """
                LOAD_CONST      1 (42)
                RETURN_VALUE
        """
        co.check_bytecodes(asm)

if __name__ == '__main__':
    unittest.main()
