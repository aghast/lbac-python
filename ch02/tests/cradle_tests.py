#!/usr/bin/env python
# vim: set fileencoding=utf8
"""
    ch02.tests.cradle_tests.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Specifies the behavior of the cradle functions.

    :copyright: 2013 by Austin Hastings, see AUTHORS for more details.
    :license: GPL v3+, see LICENSE for more details.
"""
from io import StringIO
import sys
import unittest

from ch02 import cradle as compiler

class TestCradle(unittest.TestCase):

    def assertExpr(self, text, result):
        self.stdin = StringIO(text)
        want = "Result: %d" % int(result)
        compiler.init(inp=self.stdin, out=self.stdout, err=self.stderr)
        compiler.compile()
        output = self.stdout.getvalue().split("\n")[-2]
        self.assertEqual(output, want)

    def setUp(self):
        self.stdout = StringIO()
        self.stderr = StringIO()

    def test_abort(self):
        compiler.init(inp=StringIO(), out=self.stdout, err=self.stderr)
        with self.assertRaises(SystemExit):
            compiler.abort('hello')
        self.assertEqual(self.stderr.getvalue(), "\nhello\n")
        self.assertEqual(self.stdout.getvalue(), "")

    def test_error(self):
        compiler.init(inp=StringIO(), out=self.stdout, err=self.stderr)
        compiler.error('whoops')
        self.assertEqual(self.stderr.getvalue(), "\nwhoops\n")
        self.assertEqual(self.stdout.getvalue(), "")

    def test_expected(self):
        compiler.init(inp=StringIO(), out=self.stdout, err=self.stderr)
        with self.assertRaises(SystemExit):
            compiler.expected('better')
        self.assertEqual(self.stderr.getvalue(), "\n'better' expected.\n")

    def test_get_char(self):
        inp = StringIO('abc')
        compiler.init(inp=inp, out=self.stdout, err=self.stderr)
        self.assertEqual(compiler.get_char(), 'a')
        self.assertEqual(compiler.get_char(), 'b')
        self.assertEqual(compiler.get_char(), 'c')

    def test_get_number(self):
        inp = StringIO('12z')
        compiler.init(inp=inp, out=self.stdout, err=self.stderr)
        self.assertEqual(compiler.get_number(), '1')
        self.assertEqual(compiler.get_number(), '2')

        with self.assertRaises(SystemExit):
            compiler.get_number()
        self.assertEqual(self.stderr.getvalue(), "\n'Number' expected.\n")

    def test_get_word(self):
        inp = StringIO('ab1')
        compiler.init(inp=inp, out=self.stdout, err=self.stderr)
        self.assertEqual(compiler.get_word(), 'a')
        self.assertEqual(compiler.get_word(), 'b')

        with self.assertRaises(SystemExit):
            compiler.get_word()
        self.assertEqual(self.stderr.getvalue(), "\n'Word' expected.\n")

    def test_match(self):
        inp = StringIO('mo')
        compiler.init(inp=inp, out=self.stdout, err=self.stderr)
        self.assertEqual(compiler.Peek, 'm')
        compiler.match('m')
        self.assertEqual(compiler.Peek, 'o')
        with self.assertRaises(SystemExit):
            compiler.match('n')
        self.assertEqual(self.stderr.getvalue(), "\n'n' expected.\n")

    def test_emit(self):
        compiler.init(inp=StringIO(), out=self.stdout, err=self.stderr)
        compiler.emit('abc')
        self.assertEqual(self.stdout.getvalue(), 'abc')

    def test_emitln(self):
        compiler.init(inp=StringIO(), out=self.stdout, err=self.stderr)
        compiler.emitln('123')
        self.assertEqual(self.stdout.getvalue(), "123\n")

if __name__ == '__main__':
    unittest.main()

