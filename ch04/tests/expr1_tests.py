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

from ch04 import expr1 as compiler
from ch04.bytecode import instructions_match

class TestCompiler(unittest.TestCase):

    def assertExpr(self, text, asm):
        compiler.init(inp=StringIO(text))
        co = compiler.compile()
        instructions_match(co, asm)

    def test_constant(self):
        asm = """
            LOAD_CONST 1 (7)
            RETURN_VALUE
        """
        self.assertExpr("7", asm)

    def test_add(self):
        asm = """
            LOAD_CONST 1 (1)
            LOAD_CONST 2 (8)
            BINARY_ADD
            RETURN_VALUE
        """
        self.assertExpr("1+8", asm)

    def test_subtract(self):
        asm = """
            LOAD_CONST 1 (8)
            LOAD_CONST 2 (3)
            BINARY_SUBTRACT
            RETURN_VALUE
        """
        self.assertExpr("8-3", asm)

    def test_multiply(self):
        asm = """
        """
        self.assertExpr("3*2", asm)

    def test_divide(self):
        asm = """
            LOAD_CONST 1 (3)
            LOAD_CONST 2 (2)
            BINARY_FLOOR_DIVIDE
            RETURN_VALUE
        """
        self.assertExpr("3/2", asm)

    def test_multiple_binops(self):
        asm = """
            LOAD_CONST 1 (1)
            LOAD_CONST 2 (2)
            LOAD_CONST 3 (4)
            BINARY_MULTIPLY
            LOAD_CONST 4 (3)
            BINARY_FLOOR_DIVIDE
            BINARY_ADD
            RETURN_VALUE
        """
        self.assertExpr("1+2*4/3", asm)

    def test_paren_expr(self):
        asm = """
            LOAD_CONST 1 (1)
            LOAD_CONST 2 (2)
            BINARY_ADD
            LOAD_CONST 3 (3)
            LOAD_CONST 4 (4)
            BINARY_ADD
            BINARY_MULTIPLY
            RETURN_VALUE
        """
        self.assertExpr("(1+2)*(3+4)", asm)

    def test_unary_minus(self):
        asm = """
            LOAD_CONST 1 (3)
            UNARY_NEGATIVE
        """
        self.assertExpr("-3", asm)

    def test_unary_plus(self):
        asm = """
            LOAD_CONST 1 (8)
            RETURN_VALUE
        """
        self.assertExpr("+8", asm)


if __name__ == '__main__':
    unittest.main()
