#!/usr/bin/env python
# vim: set fileencoding=utf8
"""
    ch02.expr1
    ~~~~~~~~~~~

    My version of the first expression-parsing code for chapter 2.

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
    result = expression()
    emitln("Result: %d" % result)

_Addops_sw = {
    '+': lambda x,y: x+y,
    '-': lambda x,y: x-y,
}

_Mulops_sw = {
    '*': lambda x,y: x*y,
    '/': lambda x,y: x//y,
}

_Unaryops_sw = {
    '-': lambda x: -x,
    '+': lambda x: +x,
    '~': lambda x: ~x,
}


def expr_add():
    """
    Handle additive sub-expressions. Call expr_mul() as needed.
    """
    result = expr_mul()
    while Peek in _Addops_sw:
        num1 = result
        op = get_char()
        num2 = expr_mul()
        fn = _Addops_sw[op]
        result = fn(result, num2)
        emitln("%d %s %d = %d" % (num1, op, num2, result))
    return result

def expr_atom():
    """
    Handle 'atomic' expression elements in one place: numbers,
    variables, and (sub-expressions).
    """
    if Peek == '(':
        match('(')
        result = expression()
        match(')')
    elif Peek.isdigit():
        result = int(get_number())
    elif Peek.isalpha():
        raise NotImplementedError("No variables yet.")
    else:
        expected("Expression Atom")

    return result

def expr_mul():
    """
    Handle multiplicative sub-expressions.
    """
    result = expr_unary()
    while Peek in _Mulops_sw:
        num1 = result
        op = get_char()
        num2 = expr_unary()
        fn = _Mulops_sw[op]
        result = fn(result, num2)
        emitln("%d %s %d = %d" % (num1, op, num2, result))
    return result

def expr_unary():
    """
    Handle unary operators, like +3 or -9.
    """
    if Peek in _Unaryops_sw:
        op = get_char()
        fn = _Unaryops_sw[op]
        num = expr_unary()
        result = fn(num)
        emitln("unary:%s(%d) = %d" %(op, num, result))
    else:
        result = expr_atom()
    return result

def expression():
    result = expr_add()
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

