#!/usr/bin/env python
# vim: set fileencoding=utf8
"""
    ch01.cradle
    ~~~~~~~~~~~

    A framework of commonly-used routines for the Let's Build a Compiler (in Python)!
    project.

    :copyright: 2013 by Austin Hastings, see AUTHORS for more details.
    :license: GPL v3+, see LICENSE for more details.
"""
import sys
import io
import pdb

##### Error handling

def abort(msg):
    pass

def error(msg):
    pass

def expected(what):
    pass

##### Input handling

def get_char():
    pass

def get_number():
    pass

def get_word():
    pass

def match(ch):
    pass

##### Output functions

def emit(text):
    pass

def emitln(text):
    pass

##### Processing

def init(inp=None):
    pass

def main():
    print("Enter your code on a single line. Enter '.' by itself to quit.")
    while True:
        line = input()
        if line == ".":
            break
        init(inp=StringIO(line))
        compile()

if __name__ == '__main__':
    main()

