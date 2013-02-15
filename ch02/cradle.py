#!/usr/bin/env python
# vim: set fileencoding=utf8
"""
    ch02.cradle
    ~~~~~~~~~~~

    A framework of commonly-used routines for the Let's Build a Compiler (in
    Python)!  project, chapter 2. This file is the same as the ch01/ch01.py
    file I wrote to satisfy the chapter 1 test cases. If you have your own
    version that passes the tests, copy it over this one.

    :copyright: 2013 by Austin Hastings, see AUTHORS for more details.
    :license: GPL v3+, see LICENSE for more details.
"""
import sys
import io
import pdb

##### Error handling

def abort(msg):
    """
    Report an error and raise a SystemExit exception.
    """
    error(msg)
    sys.exit(1)

def error(msg):
    """
    Report an error. Wrap the message in newlines to separate it from other output.
    """
    sys.stderr.write("\n" + msg + "\n")

def expected(what):
    """
    Report on an input value not present. Abort.
    """
    abort("'%s' expected." % what)

##### Input handling

_Input = None
Peek = None
"""
Stores the input look-ahead character. This is the next character in the input
stream, and will be returned by get_char().

For those with a 'C' background, using this variable avoids having to deal with
`ungetc()` all the time.
"""

def get_char():
    """
    Advance the input to the next character. Return the character consumed,
    or None. Note that this function changes `Peek`, and returns the *old*
    value of `Peek`.
    """
    global Peek
    result = Peek
    Peek = _Input.read(1) if sys.stdin.readable() else None
    return result

def get_number():
    """
    Expect that the next input will be a number. Read and return
    the (single-digit) number. Abort if not found..
    """
    dig = get_char()
    if not dig.isdigit():
        expected('Number')
    return dig

def get_word():
    """
    Expect that the next input will be a word - either an identifier or
    a key word. Read and return the (single-character) word. Abort if
    not found.
    """
    word = get_char()
    if not word.isalpha():
        expected('Word')
    return word

def match(ch):
    """
    Require that the next input read be the character given as a parameter.
    Abort if not found.
    """
    if get_char() != ch:
        expected(ch)

##### Output functions

def emit(text):
    sys.stdout.write(text)

def emitln(text):
    sys.stdout.write(text + "\n")

##### Processing

def init(inp=None):
    global _Input
    _Input = inp
    get_char()

def compile():
    pass

def main():
    print("Enter your code on a single line. Enter '.' by itself to quit.")
    while True:
        line = input()
        if line == ".":
            break
        init(inp=io.StringIO(line))
        compile()

if __name__ == '__main__':
    main()

