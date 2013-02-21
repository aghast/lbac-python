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
        self.co_cellvars = []
        self.co_code = bytearray()
        self.co_consts = [None]
        self.co_firstlineno = 1
        self.co_freevars = []
        self.co_names = []
        self.co_varnames = []
        self.co_offset = 0
        self._fixups_done = False
        self._fixups = []

        if from_fn is not None:
            c = from_fn.__code__
            self.co_code = c.co_code
            self.co_consts = c.co_consts
            self.co_firstlineno = c.co_firstlineno

    def __str__(self):
        return ''

    def _do_fixups(self):
        if self._fixups_done:
            return

        self._fixups_done = True

        def freevar_fixup(offset):
            co_code = self.co_code
            if offset > len(co_code) - 3:
                raise IndexError("Offset %d too large for co_code (%d)" % offset, len(co_code))
            opnum = co_code[offset]
            argval = co_code[offset + 1] | (co_code[offset + 2] << 8)
            print("freevar fixup: offset %d, argval %d" % (offset, argval))
            argval = len(self.co_cellvars) + 65535 - argval
            print("freevar fixup: argval fixed to %d" % argval)
            self._rewrite(offset, opnum, argval)

        def jump_label_fixup(offset):
            """Fixup jumps. The argument field will be the index into
            self._jump_fixups, which should have the correct target
            offset."""
            co_code = self.co_code
            if offset >= len(co_code) - 3:
                raise IndexError("Offset %d too large for co_code (%d)" % offset, len(co_code))
            opnum = co_code[offset]
            argval = co_code[offset + 1] | (co_code[offset + 2] << 8);
            target = self._jump_targets[argval]
            if opnum in opcode.hasjrel:
                delta = target - (offset + 3)
                if delta > 0xFFFF:
                    raise ValueError("Cannot fixup jump: delta requires EXTENDED_ARG")
                co_code[offset + 1] = delta & 0xFF
                co_code[offset + 2] = (delta >> 8) & 0xFF
            else:
                if target > 0xFFFF:
                    raise ValueError("Cannot fixup jump: target requires EXTENDED_ARG")
                co_code[offset + 1] = target & 0xFF
                co_code[offset + 2] = (target >> 8) & 0xFF

        op_fixup_funcs = [ None ] * 256
        for num in opcode.hasfree:
            op_fixup_funcs[num] = freevar_fixup

        print("Fixups:")
        print("Before: " + repr(self.co_code))
        for offset in reversed(self._fixups):
            opnum = self.co_code[offset]
            if op_fixup_funcs[opnum] is not None:
                op_fixup_funcs[opnum](offset)
        print("After : " + repr(self.co_code))

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

    def _find_cell_or_free(self, name, is_store=False):
        """
        Find the correct slot index# for variable 'name' in the cell or
        free variables tables. If name is not in either table, it will
        be added. If is_store is True, and name is not found, then this
        is the initial store to the variable, and so `cell` is assumed.
        Otherwise, `free` is used.

        Return: the index number to use, encoded for later fixup.
        """
        print("cell or free: %s?" % name)
        try:
            index = self.co_cellvars.index(name)
            print("Got cellvar: %d" % index)
        except ValueError:
            try:
                index = self.co_freevars.index(name)
                print("Got freevar: %d" % index)
            except ValueError:
                index = len(self.co_freevars)
                print("Adding freevar: %d" % index)
                self.co_freevars.append(name)
            index = 65535 - index
            self._fixups.append(self.co_offset)
        if len(self.co_cellvars) + len(self.co_freevars) > 65535:
            raise RangeError("Too many free+cell vars. Need better algorithm")
        print("returning index: %d"%index)
        return index

    def _rewrite(self, offset, opnum, arg=None):
        co_code = self.co_code
        was_arg = (co_code[offset] >= self.HAVE_ARGUMENT)

        print("Rewrite: @%d, %d(%s)" % (offset, opnum, repr(arg)))
        if was_arg:
            if opnum >= self.HAVE_ARGUMENT:
                if arg is None:
                    raise ValueError("Code %d requires an argument, " \
                        "but None provided" % opnum)
                elif arg > 0xFFFF:
                    raise ValueError("Argument %d is too large" % arg)
                arg1 = arg & 0xFF
                arg2 = (arg >> 8) & 0xFF
            else:
                arg1 = arg2 = self._Op_number['NOP']
            co_code[offset:offset+3] = (opnum, arg1, arg2)
        else:
            if opnum >= self.HAVE_ARGUMENT:
                raise ValueError("Opcode %d at offset %d has no arguments to replace" % co_code[offset], offset)
            else:
                co_code[offset] = opnum

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
            index = self._find_cell_or_free(arg, instr.startswith('STORE'))
            self._emit(op_num, index)

        elif op_num in opcode.hasjabs:
            # Use absolute addressing?
            self._emit(op_num, arg)

        elif op_num in opcode.hasjrel:
            self._emit(op_num, arg)

        elif op_num in opcode.haslocal:
            # The *_FAST opcodes
            try:
                index = self.co_varnames.index(arg)
            except ValueError:
                index = len(self.co_varnames)
                self.co_varnames.append(arg)
            self._emit(op_num, index)

        elif op_num in opcode.hasname:
            try:
                index = self.co_names.index(arg)
            except ValueError:
                index = len(self.co_names)
                self.co_names.append(arg)
            self._emit(op_num, index)
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

    _Argval_lookup = {
            'LOAD_CONST': lambda s,o: s.co_consts[o],
            'LOAD_CLOSURE': lambda s,o: s.co_cellvars[o] if o < len(s.co_cellvars) else s.co_freevars[o - len(s.co_cellvars)],

            'DELETE_ATTR' : lambda s,o: s.co_names[o],
            'LOAD_ATTR'   : lambda s,o: s.co_names[o],
            'STORE_ATTR'  : lambda s,o: s.co_names[o],

            'DELETE_DEREF': lambda s,o: s.co_cellvars[o] if o < len(s.co_cellvars) else s.co_freevars[o - len(s.co_cellvars)],
            'LOAD_DEREF'  : lambda s,o: s.co_cellvars[o] if o < len(s.co_cellvars) else s.co_freevars[o - len(s.co_cellvars)],
            'STORE_DEREF' : lambda s,o: s.co_cellvars[o] if o < len(s.co_cellvars) else s.co_freevars[o - len(s.co_cellvars)],

            'DELETE_FAST': lambda s,o: s.co_varnames[o],
            'LOAD_FAST': lambda s,o: s.co_varnames[o],
            'STORE_FAST': lambda s,o: s.co_varnames[o],

            'DELETE_GLOBAL': lambda s,o: s.co_names[o],
            'LOAD_GLOBAL': lambda s,o: s.co_names[o],
            'STORE_GLOBAL': lambda s,o: s.co_names[o],

            'DELETE_NAME': lambda s,o: s.co_names[o],
            'LOAD_NAME': lambda s,o: s.co_names[o],
            'STORE_NAME': lambda s,o: s.co_names[o],

            'IMPORT_FROM' : lambda s,o: s.co_names[o],
            'IMPORT_NAME' : lambda s,o: s.co_names[o],
        }

    def check_bytecodes(self, assembly):
        """
        Check bytecodes against an assembly listing from dis.
        """
        if not self._fixups_done:
            self._do_fixups()

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

            if match['offset'] is not None:
                assert int(match['offset']) == offset
            assert match['opcode'] == opcode, \
                    "Expected opcode: %s, got %s at line %s" % (match['opcode'], opcode, asm)
            if match['arg'] is not None:
                assert int(match['arg']) == args[0], \
                    "Expected arg: %s, got %d at line %s" % (match['arg'], args[0], asm)

            mval = match['value']
            if mval is not None:
                const = self._Argval_lookup[opcode](self, args[0])
                if mval.startswith("'") or mval.startswith('"'):
                    assert isinstance(const, str)
                    assert const == mval[1:-1]
                else:
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

    def finalize():
        if not self._fixups_done:
            self._do_fixups()
