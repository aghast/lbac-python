#!/usr/bin/env python
# vim: set fileencoding=utf8
"""
    ch01.tests.cradle_tests.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Specifies the behavior of the cradle functions.

    :copyright: 2013 by Austin Hastings, see AUTHORS for more details.
    :license: GPL v3+, see LICENSE for more details.
"""
from io import StringIO
import sys
import unittest

from ch01 import ch01 as cradle

class TestCradle(unittest.TestCase):

    def setUp(self):
        self.stdout = StringIO()
        self.stderr = StringIO()
        sys.stdout = self.stdout
        sys.stderr = self.stderr

    def test_abort(self):
        with self.assertRaises(SystemExit):
            cradle.abort('hello')
        self.assertEqual(self.stderr.getvalue(), "\nhello\n")
        self.assertEqual(self.stdout.getvalue(), "")

    def test_error(self):
        cradle.error('whoops')
        self.assertEqual(self.stderr.getvalue(), "\nwhoops\n")
        self.assertEqual(self.stdout.getvalue(), "")

    def test_expected(self):
        with self.assertRaises(SystemExit):
            cradle.expected('better')
        self.assertEqual(self.stderr.getvalue(), "\n'better' expected.\n")

    def test_get_char(self):
        inp = StringIO('abc')
        cradle.init(inp)
        self.assertEqual(cradle.get_char(), 'a')
        self.assertEqual(cradle.get_char(), 'b')
        self.assertEqual(cradle.get_char(), 'c')

    def test_get_number(self):
        inp = StringIO('12z')
        cradle.init(inp)
        self.assertEqual(cradle.get_number(), '1')
        self.assertEqual(cradle.get_number(), '2')

        with self.assertRaises(SystemExit):
            cradle.get_number()
        self.assertEqual(self.stderr.getvalue(), "\n'Number' expected.\n")

    def test_get_word(self):
        inp = StringIO('ab1')
        cradle.init(inp)
        self.assertEqual(cradle.get_word(), 'a')
        self.assertEqual(cradle.get_word(), 'b')

        with self.assertRaises(SystemExit):
            cradle.get_word()
        self.assertEqual(self.stderr.getvalue(), "\n'Word' expected.\n")

    def test_match(self):
        inp = StringIO('mo')
        cradle.init(inp)
        self.assertEqual(cradle.Peek, 'm')
        cradle.match('m')
        self.assertEqual(cradle.Peek, 'o')
        with self.assertRaises(SystemExit):
            cradle.match('n')
        self.assertEqual(self.stderr.getvalue(), "\n'n' expected.\n")

    def test_emit(self):
        cradle.emit('abc')
        self.assertEqual(self.stdout.getvalue(), 'abc')

    def test_emitln(self):
        cradle.emitln('123')
        self.assertEqual(self.stdout.getvalue(), "123\n")

if __name__ == '__main__':
    unittest.main()

