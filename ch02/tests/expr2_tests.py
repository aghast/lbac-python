#!/usr/bin/env python
# vim: set fileencoding=utf8
"""
    ch02.tests.expr1_tests
    ~~~~~~~~~~~~~~~~~~~~~~

    Unit and regression tests for expr1 module.

    :copyright: 2013 by Austin Hastings, see AUTHORS for more details.
    :license: GPL v3+, see LICENSE for more details.
"""
from io import StringIO
import sys
import unittest

from ch02 import expr1 as compiler

class TestCradle(unittest.TestCase):

    def assertExpr(self, inp, result):
        want = "Result: %d" % int(result)
        compiler.init(StringIO(inp))
        compiler.compile()
        output = self.out.getvalue().split("\n")[-2]
        self.assertEqual(output, want)

    def setUp(self):
        self._old_out = sys.stdout
        self.out = StringIO()
        sys.stdout = self.out

        self._old_err = sys.stderr
        self.err = StringIO()
        sys.stderr = self.err

    def tearDown(self):
        sys.stdout = self._old_out
        sys.stderr = self._old_err

    def test_add(self):
        self.assertExpr("1+8", 9)
        self.assertExpr("7+4", 11)

    def test_subtract(self):
        self.assertExpr("8-3", 5)
        self.assertExpr("4-4", 0)

    def test_multiply(self):
        self.assertExpr("3*2", 6)
        self.assertExpr("1*8", 8)

    def test_divide(self):
        self.assertExpr("2/2", 1)
        self.assertExpr("3/2", 1)
        self.assertExpr("6/2", 3)

    def test_read_at_eof(self):
        compiler.init(StringIO('ab'))
        self.assertEqual(compiler.get_char(), 'a')
        self.assertEqual(compiler.get_char(), 'b')
        self.assertIsNone(compiler.get_char())

    def test_simple(self):
        self.assertExpr("5", 5)
        self.assertExpr("9", 9)

    @unittest.skip
    def test_bogus_operator(self):
        with self.assertRaises(SystemExit):
            self.assertExpr("1^1", 2)
        self.assertEqual(self.err.getvalue(), "\n'BinOp' expected.\n")

    def test_multiple_binops(self):
        self.assertExpr("1+2*4/3", 3)
        self.assertExpr("8-5+3/6*9", 3)

    def test_mul_add_precedence(self):
        self.assertExpr("1+3*5", 16)
        self.assertExpr("9-6/2", 6)

    def test_paren_expr(self):
        self.assertExpr("(3)", 3)
        self.assertExpr("(1+7)", 8)
        self.assertExpr("(1+1)*5", 10)
        self.assertExpr("2+(3+1)*5", 22)

    def test_unary_sign(self):
        self.assertExpr('-1', -1)
        self.assertExpr('-2*3', -6)
        self.assertExpr('+8-3', 5)

if __name__ == '__main__':
    unittest.main()

