#!/usr/bin/env python
# vim: set et fileencoding=utf8 sts=4 sw=4 ts=4
"""
    ch04.tests.expr1_tests
    ~~~~~~~~~~~~~~~~~~~~~~

    Specifies the behavior of the ch04/expr1 compiler.

    :copyright: 2013 by Austin Hastings, see AUTHORS for more details.
    :license: GPL v3+, see LICENSE for more details.
"""
from io import StringIO
import sys
import unittest

from ch04 import expr2 as compiler
from ch04.bytecode import instructions_match

class TestCompiler(unittest.TestCase):

    def assertExpr(self, text, asm):
        compiler.init(inp=StringIO(text))
        co = compiler.compile()
        instructions_match(co, asm)

    def test_assignment(self):
        asm = """
            LOAD_CONST (7)
            STORE_FAST (x)
            LOAD_CONST (0)
            RETURN_VALUE
        """
        self.assertExpr("x=7;z0", asm)

    def test_return_var(self):
        asm = """
            LOAD_CONST (1)
            STORE_FAST (x)
            LOAD_FAST (x)
            RETURN_VALUE
        """
        self.assertExpr("x=1;zx", asm)

if __name__ == '__main__':
    unittest.main()