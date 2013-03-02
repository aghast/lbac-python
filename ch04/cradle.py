#!/usr/bin/env python
# vim: set fileencoding=utf8
"""
    ch04.cradle
    ~~~~~~~~~~~

    A framework of commonly-used routines for the Let's Build a Compiler
    (in Python)!  project, chapter 4. If you have your own version that
    passes the tests, copy it over this one.

    :copyright: 2013 by Austin Hastings, see AUTHORS for more details.
    :license: GPL v3+, see LICENSE for more details.
"""
import sys
import io
import pdb

##### Error handling

_Error = None
""" Error-reporting output stream.  """

def abort(msg):
    """
    Report an error and raise a SystemExit exception.
    """
    error(msg)
    sys.exit(1)

def error(msg):
    """
    Report an error. Wrap the message in newlines to separate it from
    other output.
    """
    _Error.write("\n" + msg + "\n")

def expected(what):
    """
    Report on an input value not present. Abort.
    """
    abort("'%s' expected." % what)

##### Input handling

_Input = None
""" Input stream.  """

Peek = None
"""
Peek stores the input look-ahead character. This is the next character
in the input stream, and will be returned by get_char().

For those with a 'C' background, using this variable avoids having to
deal with `ungetc()` all the time.
"""

def get_char():
    """
    Advance the input to the next character. Return the character consumed,
    or None. Note that this function changes `Peek`, and returns the *old*
    value of `Peek`.
    """
    global Peek
    result = Peek
    Peek = _Input.read(1) if _Input.readable() else None
    if Peek == '':
        # Handle ttys and StringIO objects: still readable but empty right now.
        Peek = None
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

_Output = None
""" Output stream for results.  """

def emit(text):
    _Output.write(text)

def emitln(text):
    _Output.write(text + "\n")

##### Processing

def init(inp=None, out=None, err=None):
    global _Input, _Output, _Error
    _Output = out if out is not None else sys.stdout
    _Error = err if err is not None else sys.stderr

    _Input = inp if inp is not None else _Input
    # 'prime the pump' to read first character, etc.
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

