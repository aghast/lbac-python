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

class CodeObject:

    def __init__(self, ref=None):
        """
        Create a new CodeObject. If `from` is set, take the values from
        the function or code object given. Otherwise, the object should
        be empty but ready to modify.
        """
        if ref is None:
            self._appended_ops = []
            self._modifiable = True
            self.co_argcount = 0
            self.co_code = bytearray()
            self.co_consts = [None, ]
            self.co_filename = '<no file>'
            self.co_firstlineno = 1
            self.co_flags = 0
            self.co_lnotab = bytearray()
            self.co_name = '<no name>'
            self.co_names = []
            self.co_nlocals = 0
            self.co_stacksize = 0
            self.co_varnames = []
        else:
            if isinstance(ref, types.CodeType):
                from_co = ref
            elif isinstance(ref, types.FunctionType):
                from_co = ref.__code__
            else:
                raise ValueError("Don't know how to handle type: %s" % type(ref))

            self._appended_ops = []
            self._modifiable = False
            self.co_argcount = from_co.co_argcount
            self.co_code = from_co.co_code
            self.co_consts = from_co.co_consts
            self.co_filename = from_co.co_filename
            self.co_firstlineno = from_co.co_firstlineno
            self.co_flags = from_co.co_flags
            self.co_lnotab = from_co.co_lnotab
            self.co_name = from_co.co_name
            self.co_names = from_co.co_names
            self.co_nlocals = from_co.co_nlocals
            self.co_stacksize = from_co.co_stacksize
            self.co_varnames = from_co.co_varnames

    def _append_invalid_opcode(self, opnum, arg):
        raise ValueError("Invalid opcode specified: %d" % opnum)

    def _append_opcode_noarg(self, opnum, arg):
        if arg is not None:
            raise ValueError("Argument provided to no-arg opcode: (%d, %s)" % (opnum, repr(arg)))
        self.append_bytecode(opnum, None)

    def _append_opcode_const(self, opnum, arg):
        value_list = self.co_consts
        try:
            arg_index = value_list.index(arg)
        except ValueError:
            arg_index = len(value_list)
            value_list.append(arg)
        self.append_bytecode(opnum, arg_index)

    def _append_opcode_compare(self, opnum, arg):
        value_list = opcode.cmp_op
        try:
            arg_index = value_list.index(arg)
        except ValueError:
            arg_index = len(value_list)
            value_list.append(arg)
        self.append_bytecode(opnum, arg_index)

    def _append_opcode_freevar(self, opnum, arg):
        raise NotImplementedError("not yet")

    def _append_opcode_jumpabs(self, opnum, arg):
        raise NotImplementedError("not yet")

    def _append_opcode_jumprel(self, opnum, arg):
        raise NotImplementedError("not yet")

    def _append_opcode_localvar(self, opnum, arg):
        raise NotImplementedError("not yet")

    def _append_opcode_name(self, opnum, arg):
        raise NotImplementedError("not yet")

    def _append_opcode_numargs(self, opnum, arg):
        raise NotImplementedError("not yet")

    _append_dispatch = [ _append_invalid_opcode ] * 256
    _append_strategy = {
            _append_opcode_noarg  : [ x for x in range(opcode.HAVE_ARGUMENT - 1) ],
            _append_opcode_compare: opcode.hascompare,
            _append_opcode_const  : opcode.hasconst,
            _append_opcode_freevar: opcode.hasfree,
            _append_opcode_jumpabs: opcode.hasjabs,
            _append_opcode_jumprel: opcode.hasjrel,
            _append_opcode_localvar: opcode.haslocal,
            _append_opcode_name   : opcode.hasname,
            _append_opcode_numargs: opcode.hasnargs,
    }

    for strategy, oplist in _append_strategy.items():
        for op in oplist:
            _append_dispatch[op] = strategy

    def append(self, opname, arg=None):
        opnum = opcode.opmap[opname]
        self._appended_ops.append((opname, opnum, arg))
        meth = self._append_dispatch[opnum].__get__(self)
        meth(opnum, arg)

    def append_bytecode(self, opnum, arg):
        if not self._modifiable:
            raise TypeError("Cannot append to unmodifiable object.")
        bytes = self.co_code
        if opnum >= opcode.HAVE_ARGUMENT:
            if arg > 0xFFFF:
                self.append_bytecode(opcode.EXTENDED_ARG, arg >> 16)
            bytes.append(opnum)
            bytes.append(arg & 0xFF)
            bytes.append((arg>>8) & 0xFF)
        else:
            bytes.append(opnum)

    def check_bytecode(self, wanted):
        print("Got bytecode: {!r}".format(self.co_code))
        pass

    def _decode_argindex(self, it, extended_arg):
        """Decodes an argument index, including support for extended_arg."""
        argindex = next(it)
        argindex |= next(it) << 8
        if extended_arg is not None:
            argindex |= extended_arg << 16
        return argindex

    def _decode_common(self, opnum, offset):
        lineno = self.get_lineno_of_offset(offset)
        labels = self.get_labels_at_offset(offset)
        opname = opcode.opname[opnum]
        return (lineno, labels, opname)

    def _decode_invalid_opcode(self, opnum, it, offset, extended_arg):
        opname = opcode.opname[opnum]
        raise ValueError("Unknown opcode '%s' at offset %d" % (opname, offset))

    def _decode_opcode_noarg(self, opnum, it, offset, extended_arg):
        """Return a tuple of (lineno, offset, (labels), opnum, opname,
        argindex, argvalue)."""
        lineno, labels, opname = self._decode_common(opnum, offset)
        argvalue = argindex = None
        return (lineno, offset, labels, opnum, opname, argindex, argvalue)

    def _decode_opcode_hasconst(self, opnum, it, offset, extended_arg):
        """Return a tuple of (lineno, offset, (labels), opnum, opname,
        argindex, argvalue)."""
        lineno, labels, opname = self._decode_common(opnum, offset)
        argindex = self._decode_argindex(it, extended_arg)
        argvalue = self.co_consts[argindex]
        return (lineno, offset, labels, opnum, opname, argindex, argvalue)

    def _decode_opcode_compare(self, opnum, it, offset, extended_arg):
        """Return a tuple of (lineno, offset, (labels), opnum, opname,
        argindex, argvalue)."""
        lineno, labels, opname = self._decode_common(opnum, offset)
        argindex = self._decode_argindex(it, extended_arg)
        argvalue = opcode.cmp_op[argindex]
        return (lineno, offset, labels, opnum, opname, argindex, argvalue)

    def _decode_opcode_const(self, opnum, it, offset, extended_arg):
        """Return a tuple of (lineno, offset, (labels), opnum, opname,
        argindex, argvalue)."""
        lineno, labels, opname = self._decode_common(opnum, offset)
        argindex = self._decode_argindex(it, extended_arg)
        argvalue = self.co_consts[argindex]
        return (lineno, offset, labels, opnum, opname, argindex, argvalue)

    def _decode_opcode_freevar(self, opnum, it, offset, extended_arg):
        """Return a tuple of (lineno, offset, (labels), opnum, opname,
        argindex, argvalue)."""
        raise NotImplementedError("not yet")

    def _decode_opcode_jumpabs(self, opnum, it, offset, extended_arg):
        """Return a tuple of (lineno, offset, (labels), opnum, opname,
        argindex, argvalue)."""
        raise NotImplementedError("not yet")

    def _decode_opcode_jumprel(self, opnum, it, offset, extended_arg):
        """Return a tuple of (lineno, offset, (labels), opnum, opname,
        argindex, argvalue)."""
        raise NotImplementedError("not yet")

    def _decode_opcode_localvar(self, opnum, it, offset, extended_arg):
        """Return a tuple of (lineno, offset, (labels), opnum, opname,
        argindex, argvalue)."""
        lineno, labels, opname = self._decode_common(opnum, offset)
        argindex = self._decode_argindex(it, extended_arg)
        argvalue = self.co_varnames[argindex]
        return (lineno, offset, labels, opnum, opname, argindex, argvalue)

    def _decode_opcode_name(self, opnum, it, offset, extended_arg):
        """Return a tuple of (lineno, offset, (labels), opnum, opname,
        argindex, argvalue)."""
        raise NotImplementedError("not yet")

    def _decode_opcode_numargs(self, opnum, it, offset, extended_arg):
        """Return a tuple of (lineno, offset, (labels), opnum, opname,
        argindex, argvalue)."""
        raise NotImplementedError("not yet")

    _decode_dispatch = [ _decode_invalid_opcode ] * 256
    _decode_strategy = {
        _decode_opcode_noarg  : [ x for x in range(opcode.HAVE_ARGUMENT - 1) ],
        _decode_opcode_compare: opcode.hascompare,
        _decode_opcode_const  : opcode.hasconst,
        _decode_opcode_freevar: opcode.hasfree,
        _decode_opcode_jumpabs: opcode.hasjabs,
        _decode_opcode_jumprel: opcode.hasjrel,
        _decode_opcode_localvar: opcode.haslocal,
        _decode_opcode_name   : opcode.hasname,
        _decode_opcode_numargs: opcode.hasnargs,
    }

    for strategy, oplist in _decode_strategy.items():
        for op in oplist:
            _decode_dispatch[op] = strategy

    def get_lineno_of_offset(self, offset):
        return 1

    def get_labels_at_offset(self, offset):
        return ()

    def instructions(self):
        it = iter(self.co_code)
        offset = 0
        extended_arg = None
        while True:
            opnum = next(it)
            meth = self._decode_dispatch[opnum].__get__(self)
            tpl = meth(opnum, it, offset, extended_arg)
            offset += 1
            if tpl[3] == opcode.EXTENDED_ARG:
                extended_arg = tpl[5]
            else:
                extended_arg = None
            yield tpl

_Match_line_re = re.compile(
    r'\s* (?P<lineno> \d+ )? \s* (?P<offset> \d+ )?' \
    r'\s* (?P<opname> [A-Z]\w* )' \
    r'\s* ( (?P<argindex> \d+ )' \
        r'\s* (?: \( (?P<argvalue> [^)]* ) \) )? )?',
    re.X)

def instructions_match(co, text):
    """
    Determine if a CodeObject's instruction stream matches a list of
    Python opcodes. Return True if the instructions match. Raise an
    exception if an error or mismatch occurs.
    """
    def assert_match(wanted, got, field, line):
        if wanted is None:
            return
        if wanted.isdigit():
            wanted = int(wanted)
        if wanted != got:
            raise ValueError("Mismatch in '%s' at line '%s': %s != %s" \
                % (field, line, wanted, got))
    instr = co.instructions()
    for line in text.splitlines():
        line = line.strip()
        if line == '':
            continue
        m = _Match_line_re.match(line)
        if not m:
            raise ValueError("Unparseable format in line: '%s'" % line)
        match = m.groupdict()
        try:
            (lineno, offset, labels, opnum, opname, argindex, argvalue) \
                = next(instr)
        except StopIteration:
            raise ValueError("Reached end of bytecode at line '%s'" \
                % line)
        assert_match(match['offset'], offset, 'offset', line)
        assert_match(match['opname'], opname, 'opname', line)
        assert_match(match['argindex'], argindex, 'argindex', line)
        if match['argvalue'] is not None:
            mval = match['argvalue']
            if mval.startswith('"') or mval.startswith("'"):
                mval = mval[1:-1]
            assert_match(mval, argvalue, 'argvalue', line)
    # If we run out of lines, return True.
    return True

#EOF
