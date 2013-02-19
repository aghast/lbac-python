#!/usr/bin/env python
# vim: set et fileencoding=utf8 sts=4 sw=4 ts=4
"""
    ch03.bytecode
    ~~~~~~~~~~~~~

    A bytecode generation module.

    :copyright: 2013 by Austin Hastings, see AUTHORS for more details.
    :license: GPL v3+, see LICENSE for more details.
"""
import opcode
import re
import types

def _no_valid_arg():
    """Sentinel value for `CodeObject.append`, which must support None
    as a valid argument value.
    """
    pass

class OpcodeIter:
    EXTENDED_ARG = opcode.EXTENDED_ARG
    HAVE_ARGUMENT = opcode.HAVE_ARGUMENT
    _Op_name = opcode.opname

    def __init__(self, barray, *, offset=0, extend_args=True):
        """Iterator over bytecode array, returning opcode tuples.
        Begins iteration at *offset.* Will automatically handle
        extending args unless extend_args is False, in which case
        the EXTEND_ARG opcodes are returned as part of the stream.
        """
        if isinstance(barray, types.FunctionType):
            barray = barray.__code__.co_code
        elif isinstance(barray, types.CodeType):
            barray = barray.co_code

        if offset != 0:
            # Make a copy. Ouch!
            self.bytes = barray[offset:]
        else:
            self.bytes = barray

        self.extend_args = extend_args
        self.offset = offset
        self.iter = iter(self.bytes)

    def __iter__(self):
        return self

    def __next__(self):
        return self.decode_op()

    def decode_op(self):
        iter = self.iter
        offset = self.offset
        opnum = next(iter)
        delta = 1
        if opnum == self.EXTENDED_ARG and self.extend_args:
            lsb = next(iter)
            msb = next(iter)
            arg_index = (msb << 24) | (lsb << 16)
            opnum = next(iter)
            delta += 3
        else:
            arg_index = 0
        opcode = self._Op_name[opnum]
        has_arg = (opnum >= self.HAVE_ARGUMENT)
        if has_arg:
            lsb = next(iter)
            msb = next(iter)
            delta += 2
            arg_index |= (msb << 8) | lsb
            result = (offset, opcode, arg_index)
        else:
            result = (offset, opcode)
        self.offset += delta
        return result

class CodeObject:
    """
    Models a Python built-in `code` object, the type returned by the
    `compile` function, for use with a code generator that needs to
    construct the objects dynamically.
    """

    EXTENDED_ARG = opcode.EXTENDED_ARG
    HAVE_ARGUMENT = opcode.HAVE_ARGUMENT

    _Op_number = opcode.opmap
    """Map an opcode name (LOAD_CONST) to a byte code."""

    _Op_name = opcode.opname
    """Map an opcode number to the opcode name."""

    _Op_has_arg = tuple( num >= opcode.HAVE_ARGUMENT for num in range(255))
    """True if opcode # takes an arg."""

    def __init__(self, from_fn=None):
        self.co_code = bytearray()
        self.co_consts = [None]
        self.co_firstlineno = 1
        self.co_offset = 0

        if from_fn is not None:
            c = from_fn.__code__
            self.co_code = c.co_code
            self.co_consts = c.co_consts
            self.co_firstlineno = c.co_firstlineno

    def __str__(self):
        return ''

    def _emit(self, code, arg=None):
        if code > 0xFF:
            raise ValueError("Code %d is not a valid opcode number" % code)
        if arg is not None and arg > 0xFFFF:
            self._emit(self._Op_number['EXTENDED_ARG'], arg >> 16)
            arg = arg & 0xFFFF
        append = self.co_code.append
        append(code)
        if arg is not None:
            append(arg & 0xFF)
            append((arg>>8) & 0xFF)
        self.co_offset = len(self.co_code)

    def append(self, instr, arg=_no_valid_arg):
        if instr not in self._Op_number:
            raise ValueError("{!r} is not a valid opop_num name".format(instr))
        op_num = self._Op_number[instr]
        has_arg = (op_num >= self.HAVE_ARGUMENT)
        if arg is _no_valid_arg and has_arg:
            raise ValueError("Opcode '%s' requires an argument" % instr)
        if op_num in opcode.hascompare:
            if arg in opcode.cmp_op:
                arg = opcode.cmp_op.index(arg)
            else:
                raise ValueError("Opcode '%s' requires compare-op argument like '<='" % instr)
            self._emit(op_num, arg)
        elif op_num in opcode.hasconst:
            try:
                arg_index = self.co_consts.index(arg)
            except ValueError:
                arg_index = len(self.co_consts)
                self.co_consts.append(arg)
            self._emit(op_num, arg_index)
        elif op_num in opcode.hasfree:
            # Not sure what these mean
            pass
        elif op_num in opcode.hasjabs:
            # Use absolute addressing?
            self._emit(op_num, arg)
        elif op_num in opcode.hasjrel:
            self._emit(op_num, arg)
        elif op_num in opcode.haslocal:
            # Search for index in local vars table
            pass
        elif op_num in opcode.hasname:
            # Search for index in names table (attributes, mainly)
            pass
        elif op_num in opcode.hasnargs:
            self._emit(op_num, arg)
        else:
            self._emit(op_num)

    _Check_line_re = re.compile(
        r'\s* (?P<lineno> \d+ )? \s* (?P<offset> \d+ )? ' \
            + r'\s* (?P<opcode> [A-Z] \w* ) \s* ' \
            + r' ( (?P<arg> \d+ ) ' \
                + '\s* (?: \( (?P<value> [^)]* ) \) )? )?',
        re.X)

    def check_bytecodes(self, assembly):
        """
        Check bytecodes against an assembly listing from dis.
        """
        it = OpcodeIter(self.co_code)
        for asm in assembly.splitlines():
            m = self._Check_line_re.match(asm)
            if not m:
                if asm.strip() == '':
                    continue
                else:
                    raise ValueError("Unrecognized asm in line: '%s'" % asm)

            match = m.groupdict()
            try:
                offset, opcode, *args = next(it)
            except StopIteration:
                raise ValueError("Reached end of bytecodes at line: '%s'" % asm)

            print("{!r}".format((offset,opcode)+tuple(args)))
            print("{!r}".format(match))

            if match['offset'] is not None:
                assert int(match['offset']) == offset
            assert match['opcode'] == opcode
            if match['arg'] is not None:
                assert int(match['arg']) == args[0]
            mval = match['value']
            if mval is not None:
                if mval.startswith("'") or mval.startswith('"'):
                    const = self.co_consts[args[0]]
                    assert isinstance(const, str)
                    assert const == mval[1:-1]
                else:
                    const = self.co_consts[args[0]]
                    compare = type(const)(mval)
                    assert const == compare, \
                        "value %s != %s" % (compare, mval)

    def dump(self):
        line_no = ''
        arg_fmt = "{:3}      {:5d} {:20s} {:5d} ({})"
        noarg_fmt = "{:3}      {:5d} {:20s}"
        for tpl in OpcodeIter(self.co_code):
            offset, opcode, *args = tpl
            if len(args):
                argindex = args[0]
                argval = self.co_consts[argindex]
                print(arg_fmt.format('', offset, opcode, argindex, argval))
            else:
                print(noarg_fmt.format('', offset, opcode))

