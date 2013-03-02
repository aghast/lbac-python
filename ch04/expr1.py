#!/usr/bin/env python
# vim: set et sts=4 sw=4 ts=4 tw=76
"""
    ch04.expr1
    ~~~~~~~~~~~

    Expression-parsing compiler with bytecode generation for chapter 4
    of `Let's Build a Compiler (in Python)!`

    :copyright: 2013 by Austin Hastings, see AUTHORS for more details.
    :license: GPL v3+, see LICENSE for more details.
"""
import sys
import io
import pdb

from bytecode import bytecode

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

_Code = None
""" CodeObject for compiled results. """

def emit(op, arg=None):
    _Code.append(op, arg)

##### Processing

def init(inp=None, out=None, err=None):
    global _Code, _Input, _Output, _Error
    _Output = out if out is not None else sys.stdout
    _Error = err if err is not None else sys.stderr
    _Input = inp if inp is not None else _Input
    # 'prime the pump' to read first character, etc.
    get_char()
    _Code = bytecode.CodeObject()

def compile():
    expression()
    emit('RETURN_VALUE')
    return _Code

def expr_add():
    match('+')
    expr_mulop()
    emit('BINARY_ADD')

def expr_addop():
    expr_mulop()
    while Peek is not None and Peek in "+-":
        if Peek == "+":
            expr_add()
        elif Peek == "-":
            expr_subtract()
        else:
            expected('AddOp')

def expr_atom():
    if Peek == '(':
        match('(')
        expression()
        match(')')
    else:
        num = int(get_number())
        emit('LOAD_CONST', num)

def expr_divide():
    match('/')
    expr_unary()
    emit('BINARY_FLOOR_DIVIDE')

def expr_mulop():
    expr_unary()
    while Peek is not None and Peek in "*/":
        if Peek == "*":
            expr_multiply()
        elif Peek == "/":
            expr_divide()
        else:
            expected('MulOp')

def expr_multiply():
    match('*')
    expr_unary()
    emit('BINARY_MULTIPLY')

def expr_subtract():
    match('-')
    expr_mulop()
    emit('BINARY_SUBTRACT')

def expr_unary():
    if Peek is not None and Peek in "+-":
        if Peek == "+":
            expr_unary_plus()
        elif Peek == "-":
            expr_unary_minus()
        else:
            expected('UnaryOp')
    else:
        expr_atom()

def expr_unary_minus():
    match('-')
    expr_atom()
    emit('UNARY_NEGATIVE')

def expr_unary_plus():
    match('+')
    expr_atom()

def expression():
    expr_addop()

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

