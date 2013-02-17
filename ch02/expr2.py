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
Peek stores the input look-ahead character. This is the next character in the
input stream, and will be returned by get_char().

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
    Peek = _Input.read(1) if sys.stdin.readable() else None
    if Peek == '':
        # StringIO and tty objects can be 'readable but empty now'.
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

    _Input = inp if inp is not None else sys.stdin
    # 'prime the pump' to read first character, etc.
    get_char()

def compile():
    result = expression()
    emitln("Result: %d" % result)


def expr_add(num):
    match('+')
    num2 = expr_mulop()
    result = num + num2
    emitln(".. computed %d + %d = %d" % (num, num2, result))
    return result

def expr_addop():
    """
    Handle additive sub-expressions, with precedence.
    """
    result = expr_mulop()
    while Peek is not None and Peek in "+-":
        if Peek == "+":
            result = expr_add(result)
        elif Peek == "-":
            result = expr_subtract(result)
    return result

def expr_atom():
    if Peek == '(':
        match('(')
        result = expression()
        match(')')
    elif Peek.isdigit():
        result = int(get_number())
    elif Peek.isalpha():
        raise NotImplementedError("No variables yet.")
    return result

def expr_divide(num):
    match('/')
    num2 = expr_atom()
    result = num // num2
    emitln(".. computed %d // %d = %d" % (num, num2, result))
    return result

def expr_mulop():
    """
    Handle multiplicative sub-expressions, with precedence.
    """
    result = expr_atom()
    while Peek is not None and Peek in "*/":
        if Peek == "*":
            result = expr_multiply(result)
        elif Peek == "/":
            result = expr_divide(result)
    return result

def expr_multiply(num):
    match('*')
    num2 = expr_atom()
    result = num * num2
    emitln(".. computed %d * %d = %d" % (num, num2, result))
    return result

def expr_subtract(num):
    match('-')
    num2 = expr_mulop()
    result = num - num2
    emitln(".. computed %d - %d = %d" % (num, num2, result))
    return result

def expression():
    result = expr_addop()
    return result

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

