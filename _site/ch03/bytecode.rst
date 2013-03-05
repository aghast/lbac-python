.. vim: set tw=76 ts=4 sw=4 et

Bytecode Generation
===================

Early in the last chapter we had to choose between adding more functionality
to our expression parser and generating some kind of executable code with
what we already had. We expanded the parser, with a promise to come back to
code generation 'later'. Well, it's later.

In the original series, Crenshaw chose to generate machine code for a
Motorola 68K CPU running SK*DOS -- a system that was pretty much obsolete
when he released the first article.  I suppose I could do the same thing,
but how would we be able to test?  I need to find a target architecture that
everyone has available to them, no matter what kind of machine they are
using to follow along.  Also, it would be nice if it wasn't a total pain in
the ass to run our generated code.

The solution is pretty obvious, to me. And I hope it won't bother you too
much: I've chosen to stay inside the Python environment, and focus on
generating Python byte codes. Specifically, what is called CPython -- the
interpreter written in C and (I hope) available on almost every system.

There are other Python VM's: Jython compiles Python down to the byte codes
used by the Java VM. Iron Python compiles Python down to the .NET CLR. But
I'm going to assume that if you have one of those systems, you probably also
have the ability to obtain a CPython package.

Learning the Target Architecture
--------------------------------

Unfortunately, there is no *thorough* documentation about the workings of the
Python VM. There is no "Architecture Reference Manual" and no "Assembly
Programmer's Guide" for the Python VM, the way there are for concrete CPUs
and the JVM.

Instead, there is the source code. And some articles available online. And,
of course, you have a copy of the VM available on you desktop if you need a
definitive answer.  I'm going to point you at a couple of references, and
one really good resource. After that, it will be learning-by-doing all over
again.

First, there's a copy of the op-code list in the documentation for the
:mod:`dis` module. And there's a good set of articles written by
Yaniv Aknin that details some of the internal workings of the interpreter.
[#innards]_

Next, there are the :mod:`dis` module functions ``dis`` and ``show_code``,
and the builtin ``compile`` function. Taken together, these are a great
resource to show how a "working" compiler generates bytecode.

Getting Started
---------------

Here's a good way to get started. Fire up your python interpreter in
a console window::

    Python 3.3.0 (default, Nov 23 2012, 10:26:01)
    [GCC 4.2.1 Compatible Apple Clang 4.1 ((tags/Apple/clang-421.11.66))] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>>

At the prompt, first define a simple function::

    >>> def return42():
    ...     return 42
    ...
    >>>

 Next, import the two functions `dis` and `show_code` from the `dis` module
 as `da` and `sc`. Then run both functions on `return42`::

    >>> from dis import dis as da, show_code as sc
    >> da(return42)
      2           0 LOAD_CONST               1 (42)
                  3 RETURN_VALUE
    >>> sc(return42)
    Name:              return42
    Filename:          <stdin>
    Argument count:    0
    Kw-only arguments: 0
    Number of locals:  0
    Stack size:        1
    Flags:             OPTIMIZED, NEWLOCALS, NOFREE
    Constants:
       0: None
       1: 42
    >>>

This is a great way to learn how to generate byte codes for various
situations. And it's good to have an idea exactly which flags and values
should be set when we are defining code for the interpreter.

Right now you should define some test functions containing various control
structures. See what the byte code looks like for things like an if
statement, a while loop, a print statement and the like. See what happens
when a function takes parameters. You'll need to feel comfortable with the
"define and dump" approach we're taking to learning about the VM here.

Explaining the VM
-----------------

There are a lot of VMs in the world today. The Java VM is probably the most
famous, but pretty much every scripting language (Perl, Python, Ruby)
defines a VM, as does the Microsoft .NET environment. Most (but not all) of
these VMs use what is called a *stack architecture.*

A *stack* is a concept in computer science also called a LIFO queue. (LIFO
stands for "Last In, First Out".) The premise is that there is a queue or
list of items being managed by the stack, in such a way that only the most
recently added item is available to viewing or consumption.

Consider a queue of people buying tickets at a cinema. There may be some
ropes or rails holding it in shape and preventing people from stepping into
(or out of) the middle of the queue. Typically, the tail extends towards the
doors of the cinema (and sometimes right outside!) while the head of queue
is near the ticket booth(s). When a ticket seller becomes available, they call
out "next!" and the person at the head of the queue steps up to buy tickets.

This is an example of a FIFO queue, short for "First In, First Out". People
add themmselves to the tail of the queue, and buy tickets when they reach
the head of the queue. Nobody else can buy tickets, and people in the queue
cannot easily step out, or change position, until they reach the head.

Next consider a street passing through a retail district. In smaller towns,
there will be curb-side parking along the edge of the street, with cars
facing parallel to the flow of traffic. This is the source of the dreaded
"parallel parking" part of the driver's exam. In such a scenario, cars can
pull in to any unoccupied parking space (if the driver passed that part of
the exam!) and cars can pull out of any parking space, without regard to
other cars parked nearby.

This is an example of a random-access array. The cars are in a definite
"shape" or array. It is possible to assign numbers to the parking
spaces -- for billing, perhaps. But any space can be empty or full at any
time, and drivers can choose to "store" their car into any open space
without regard for where the space is.

Finally, consider a deck of cards. If you turn the deck so that the faces
are up, and then set the deck on the table in front of you, you will have an
example of a stack. You can see only the card at the "top" of the stack. You
can add cards only at the top of the stack. You can remove cards only by
taking them from the top of the stack -- Last In, First Out. Everything you do
must be relative to the top of the stack.

This is the model that the Python VM uses internally for storing data that
it will operate on. There are no 'registers'. There is only a stack. Data
can be fetched from variables and placed on top of the stack. Data that is
on top of the stack can be sent off to be stored in a variable. Operations
like add and subtract are performed only using items on the stack.

For example, let's write some simple Python code and then disassemble it, as
we did before. Here's a function that adds a constant to a number passed in
as a parameter::

    def add20(x):
        return x+20

If we define and dump that code, we get this:

    >>> da(add20)
      2           0 LOAD_FAST                0 (x)
                  3 LOAD_CONST               1 (20)
                  6 BINARY_ADD
                  7 RETURN_VALUE

Roughly translated, the code reads as follows:

1. Read the value from variables[0] (aka 'x') and push it on the stack.
2. Load the constant from constants[1] (aka 20) and push it on the stack.
3. Add together the two numbers at the top of the stack, and push the answer
   on the stack.
4. Return the value currently on top of the stack.

Back when I was young and dinosaurs roamed the earth there was a series of
Hewlett-Packard calculators that used what is called "RPN" (Reverse Polish
Notation). If you ever used one of those calculators, and had to enter your
expressions like 3,5,+,7,6,+,/ (which is RPN for "(3+5)/(7+6)"),
congratulations! -- you already know how a stack-based machine works. For the
rest of us, I'm afraid we'll have to struggle through, occasionally invoking
the disassembler to help out.

Here's how Python computes a similar expression::

    >>> def rpn(a,b,c,d):
    ...     return (a+b)/(c+d)
    ...
    >>> da(rpn)
      2           0 LOAD_FAST                0 (a)
                  3 LOAD_FAST                1 (b)
                  6 BINARY_ADD
                  7 LOAD_FAST                2 (c)
                  10 LOAD_FAST               3 (d)
                  13 BINARY_ADD
                  14 BINARY_TRUE_DIVIDE
                  15 RETURN_VALUE

Basically, that translates as "put 'a' on the stack; put 'b' on the stack;
add them; put 'c' on the stack; put 'd' on the stack; add them; divide
what's on the stack; return what's on the stack," which is just about
exactly the same as the steps on that HP calculator.

The Inner Workings
------------------

Spend some time reading the descriptions of the :func:`compile` and
:func:`exec` functions in the on-line Python documentation. You'll find
that *code objects* are the low-level items that are generated by the
compiler, and are accepted by the bytecode evaluator.

Take a look at the documentation for the :func:`inspect` function.
You'll find a list of the internal fields for the various builtin types,
including code objects.

What I have learned from the various sources I have already mentioned is
that the `function` and `method` objects are some kind of internal
book-keeping objects. All the "real" details of bytecode storage live in the
`code` object, which underlies all functions except for the built-in ones.

The Python VM compiles just about everything as a code object. Defined
functions, obviously, but also `module` and `class` definitions. The command
line interpreter also compiles every single line, or group of lines, as a
separate module (which is a code object).

In fact, there doesn't seem to be any way of executing instructions without
using a code object -- which is fine, it shows us where we will want to focus
our efforts.

Available Libraries
-------------------

I did a search for available libraries. There are a few libraries available
for Python 2. In particular, the BytecodeAssembler module by Phillip J. Eby,
and the byteplay package by Noam Yorav-Raphael appear to do some of what we
need done. Unfortunately, they are both targeted at Python 2, do not offer
Python 3 support, and depend enough on metaprogramming and other weirdness
that I didn't feel comfortable trying to do a quick port.  So instead, we're
going to have to develop something to help us generate code objects.

Rolling our Own
---------------

In order to develop our own library, we will first need a list of opcode
data. Some of that is available in the online references, particularly in
the documentation of the :mod:`dis` module. But like a lot of VMs, the
most complete specification is the source code itself. There are plenty of
copies of the Python source code available on the web. The code we will be
most interested in lives in a file called `Python/ceval.c`. That is where
the bytecode interpreter lives.

The data that seems most obvious to me is the name, opcode number (available
in the :mod:`opcode` module), and whether or not the opcode takes an
argument. Reading the opcode list (from the :mod:`dis` module
documentation) reveals the interesting fact that there is a defined constant
`HAVE_ARGUMENT` that divides the opcodes into those with and those without
arguments.

Given that we know whether an opcode takes an argument or not, we should be
able to write out the correct encoding to a byte array. The byte array could
then become the co_code member of the code object we are going to generate,
and we can then invoke the code we have generated.  Well, there are a few
details to take care of, first. (Surprise!)

There are several lists associated with code objects. First, there is the
list of constants. I'm sure you noticed the strange format of the
`LOAD_CONST` opcodes we have dumped. They looked like this, remember::

    >>> da(return42)
      2           0 LOAD_CONST               1 (42)
                  3 RETURN_VALUE

The apparent argument to LOAD_CONST is '1', with a note attached that it
represents the value 42. This is because all bytecode arguments are 16-bit
integers. There is no provision for constants that are strings, or floating
point numbers, or lists, or other code objects. Byte code arguments are
always integers.

Secretly, these integers are actually indices into a giant Python *tuple* (a
fixed, immutable array) that contains all the constants for this code
object. So each code object we define will actually need two data
structures: a string of byte codes, and a list of constants.

But we're not done yet. In addition to the constants, there are various data
structures dealing with names used by the code object. Names are not
strings -- if you try to print `"Hello, world!",` you are using a string
constant.  Instead, names are stored in one of the variable-related tuples:
`co_varnames, co_cellvars, co_freevars,` or `co_names.` See the Python's
Innards [#innards]_ series for more details.

What does all this mean to us? Well, it means that for simple tasks like
handling constants, we will need to manage the two data structures already
discussed -- the bytecode and the constants tuple. For more complex tasks
involving variables or object member data, we will have to deal with even
more. Since we haven't done anything with variables just yet, I think we can
put off worrying about it for a while.

Writing a Test Case
-------------------

Let's pretend we have the code already written. Using it looks something
like this::

    co = CodeObject()
    co.append('LOAD_CONST', 42)
    co.append('RETURN_VALUE')

How do we test that? What format should we use that is human-writable and
can express the desired result?

I think we should use a format that is close to that generated by the
:func:`dis` function. First, because it's basically an assembly language
format, and second, because a lot of our tests are going to come from
dumping what the Python compiler generates. Something like this::

    from ch03.bytecode import CodeObject

    class TestBytecode(unittest.TestCase):
        def test_return42(self):
            co = CodeObject()
            co.append('LOAD_CONST', 42)
            co.append('RETURN_VALUE')
            expected = """
                LOAD_CONST      1 (42)
                RETURN_VALUE
            """
            self.assertInstructions(co, expected)

It will get harder and harder to specify the entire compiled bytecode
string. As we get deeper and deeper into writing a compiler, there will be
more and more 'setup' code that we don't care about but have to have in
order to put the compiler in the state we require.  Something like "does our
recursive call in an if-statement get converted to tail-recursion when we're
inside a method with three parameters in a class with multiple inheritance?"
We may eventually want to assert only a small subset of the code.

And we will probably get the constant and name indices wrong, since those
will be allocated by the compiler in some order that makes sense to it, not
necessarily to us. So eventually, we will want to be a little flexible in
our specification language. For now, though, it's good enough.

Passing the First Test Case
---------------------------

So let's write some code! I'll call the module `bytecode`, and so there
will be a `ch03/bytecode.py` and a `ch03/tests/bytecode_tests.py` file.
Also, create an empty `ch03/__init__.py` file to make importing work.
We'll keep the test case we have already written. Not surprisingly, it won't
pass at first. ::

    import unittest
    from ch03 import bytecode

    class TestBytecode(unittest.TestCase):

        def test_return42(self):
            co = CodeObject()
            co.append('LOAD_CONST', 42)
            co.append('RETURN_VALUE')
            expected = """
                    LOAD_CONST      1 (42)
                    RETURN_VALUE
            """
            self.assertInstrMatch(co, expected)

Before we start working on `ch03/bytecode.py` you should read the
documentation for the :mod:`opcode` module. An in particular, pay
attention to all the little lists that it provides. In the python
interpreter, look at the output of `import opcode; dir(opcode)` to see them
all together. Those constants (`HAVE_ARGUMENT`) and lists (`hasconst`,
`hasfree`) contain the details about the opcodes. The `opmap` and `opname`
variables map opcode numbers to names (`opname[x]`) and names to numbers
(`opmap['RETURN_VALUE']`). Plan to make use of all this data!

And have a look at the documentation for the :mod:`inspect` module. The
section on `code` objects details all the fields that a code object can
have. Since that is what we are going to produce, we should probably model
it.

Here's some init code::

    import opcode

    class CodeObject:

        def __init__(self, ref=None):
            """
            Create a new CodeObject. If `from` is set, take the values from
            the function or code object given. Otherwise, the object should
            be empty but ready to modify.
            """
            if ref is None:
                self._modifiable = True
                self.co_argcount = 0
                self.co_code = bytearray()
                self.co_consts = []
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

                self._modifiable = False
                self.co_argcount = co.co_argcount
                self.co_code = co.co_code
                self.co_consts = co.co_consts
                self.co_filename = co.co_filename
                self.co_firstlineno = co.co_firstlineno
                self.co_flags = co.co_flags
                self.co_lnotab = co.co_lnotab
                self.co_name = co.co_name
                self.co_names = co.co_names
                self.co_nlocals = co.co_nlocals
                self.co_stacksize = co.co_stacksize
                self.co_varnames = co.co_varnames

The `_modifiable` attribute is there to prevent trying (or succeeding!) to
modify bytecode that may have been produced by Python or some other
mechanism. Everything else comes straight from the documentation.

Now for the `append` function. We could require the user to manage the
constants table, and the other tables, separately. But that would be
horrible! So we'll automate the management as much as we can using the data
from the :mod:`opcode` module about what opcodes take what kind of
arguments. In pseudo-code::

    def append(self, opname, arg=None):
        opnum = opcode.opmap[opname]
        if op < opcode.HAVE_ARGUMENT:
            if arg is not None:
                bad argument
            else
                co_code.append(opnum)
        else:
            if argument-type(op) is 'constant':
                if arg is in self.co_consts:
                    argval = self.co_consts.index(arg)
                else:
                    argval = len(self.co_consts)
                    self.co_consts.append(arg)
            elif argument-type(op) is 'name':
                if arg is in self.co_names:
                    argval = self.co_names.index(arg)
                else:
                    argval = len(self.co_names)
                    self.co_names.append(arg)

            elif argument-type(op) is 'relative-jump' or argument_type(op) is 'absolute-jump':
                # Handle these differently
                pass

In any other language, that would be a 'switch' statement. And switching is
one of those things that tell us we are missing a class/subclass hierarchy.
So what are we missing? Well, the behavior is determined by the opcode, and
the opcode is either a string, or equivalently, a number between 0 and 255.
Some of those numbers are invalid. Others are no-arg opcodes, and still
others are opcodes that take names, or constants, or jumps, or whatever. So
there are potentially 256 different behaviors, or *strategies* that we can
access by indexing into a densely-packed array.

Let's try coding a few of those behaviors. We'll assume that each method
gets the opcode (a number), and the argument or None::

    def _append_invalid_opcode(self, opnum, arg):
        raise "Invalid opcode specified: %d" % opnum

    def _append_opcode_noarg(self, opnum, arg):
        self.append_bytecode(opnum)

    def _append_opcode_const(self, opnum, arg):
        try:
            arg_index = self.co_consts.index(arg)
        except IndexError:
            arg_index = len(self.co_consts)
            self.co_consts.append(arg)
        self.append_bytecode(opnum, arg_index)

    def _append_compare_op(self, opnum, arg):
        try:
            arg_index = opcode.cmp_op.index(arg)
        except IndexError:
            raise "Invalid compare operation: '%s'" % arg

When we express things this way, they're nice and clear. All we have to do
is populate an opcode-number-to-method table, and make sure to define all
the possible behaviors. Since we have a nice default value, we can leave
that in place until we are ready to use a particular group of opcodes.  The
class definition code can handle the table, since this behavior won't change
from object to object. And we can make `append` very simple this way! I'm
going to add one more thing -- a list of the opcodes that have been appended.
We'll use this for a little bit in order to debug the appender. ::

    class CodeObject:
        # ...
        def __init__(self, ...):
            # ...
            self._appended_ops = []

        # ...
        _append_dispatch = [ _append_invalid_opcode ] * 256

        _strategy_ops = {
            _append_opcode_noarg: [x for x in range(opcode.HAVE_ARGUMENT - 1) if not opcode.opname[x].startswith('<')]
            _append_opcode_compare: opcode.hascompare,
            _append_opcode_const: opcode.hasconst,
            _append_opcode_freevar: opcode.hasfree,
            _append_opcode_jumpabs: opcode.hasjabs,
            _append_opcode_jumprel: opcode.hasjrel,
            _append_opcode_localvar: opcode.haslocal,
            _append_opcode_name: opcode.hasname,
            _append_opcode_numargs: opcode.hasnargs,
        }

        for behavior, oplist in _strategy_ops.items():
            for op in oplist:
                _append_dispatch[op] = behavior

        def append(self, opname, arg=None):
            if not self._modifiable:
                raise TypeError("Cannot append to unmodifiable object.")
            opnum = opcode.opmap[opname]
            self._appended_ops.append((opname, opnum, arg))
            meth = self._append_dispatch[opnum].__get__(self, CodeObject)
            meth(opnum, arg)

        def append_bytecode(self, opnum, arg):
            bytes = self.co_code
            if opnum >= opcode.HAVE_ARGUMENT:
                if arg > 0xFFFF:
                    self.append_bytecode(opcode.EXTENDED_ARG, arg >> 16)
                bytes.append(opnum)
                bytes.append(arg & 0xFF)
                bytes.append((arg>>8) & 0xFF)
            else:
                bytes.append(opnum)

At this point we have two remaining steps to work on. First, the strategy
methods are not all implemented. That won't be a problem for our first test,
since we (think we) already have the methods implemented that the first test
case will use. Second, and more importantly, we don't have a
`assertInstructions` method at all. So let's look at what will be required
to implement that.

Fetching the Bytecodes
~~~~~~~~~~~~~~~~~~~~~~

The purpose of the `assertInstructions` method is to confirm that the bytecode
data we have in our object is consistent with the bytecodes contained in one
or more opcode strings (or tuples or something) we provide.  All of the
other fields in the CodeObject -- the co_consts, co_names, the line number
table -- all of those are maintained to support the bytecodes that are
contained in the  `bytearray` object stored in `co_code`.

Checking bytecodes, then, consists of reading through the bytecode list and
decoding each operation in sequence. Sometimes the opcodes will require an
argument, which will come from the bytecode list as well. Resolving the
argument may involve some of the other tables. Depending on the sequence,
resolving a single opcode may require one, three, or six bytes of data from
the bytecode stream.

This means that we cannot simply iterate over the bytecode data. Decoding
consumes a variable number of bytes per opcode. So we need some iterator
object between the comparison  code and the bytes.  That iterator will
have the  job of decoding the variable-length opcodes into a series of
tuples. (I considered storing the tuples, instead of bytes, but then we
couldn't use other compiled functions to initialize our objects.)

We want an opcode enumerator, or iterator, that will resolve all of fields
in a typical :mod:`dis` disassembly. That means the opcode name, the
argument index, and the argument value if it requires a lookup.

Doing all that means that the iterator will need access to our entire
CodeObject -- it's not enough to have a stream of byte codes. That's a good
argument for providing a factory method returning an iterator, instead of
just providing an iterator class. We'll try something like
`co.instructions()` in the style of `dict.keys(), dict.values(),` and
`dict.items().`

Our iterator is going to have to iterate over the bytes in the `co_code`
array doing the decode work. Given a byte to decode, we will have to
implement some kind of n-way switch on the value of the byte to determine
the decoding logic. That is a mirror image of the switch we were looking at
in the `append()` logic, above. So let's plan to solve this problem in the
same way -- use a table of methods instead of a switch or giant if/elif/else
block. We can return a tuple of: line number, offset, labels, opcode number,
opcode name, argument index, and argument value. That should make it a snap
to compare our object with a user-specified sequence of byte codes. ::

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
        raise NotImplementedError("not yet")

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
        """Return a series of tuples representing individual instructions
        decoded from self.co_code. Tuples will be composed of:
        (lineno, offset, labels, opnum, opname, argindex, argvalue)
        """
        it = iter(self.co_code)
        offset = 0
        extended_arg = None
        while True:
            opnum = next(it)
            offset += 1
            meth = self._decode_dispatch[opnum].__get__(self)
            tpl = meth(opnum, it, offset, extended_arg)
            if tpl[3] == opcode.EXTENDED_ARG:
                extended_arg = tpl[5]
            else:
                extended_arg = None
            yield tpl

At last, we come to the business of actually comparing bytecode instructions
with some kind of user input! The interface for this function will be fairly
simple: if the bytecode stream matches the user specification, it will
return true. Otherwise, it will raise an exception. Most unit testing
frameworks catch exceptions, so users can pretty safely just call our
function, or they could put in a fancy wrapper.

The job of this function is to compare a CodeObject's bytecode with an input
sequence, and determine if it matches. The input will be a CodeObject and a
long text string containing the matched instruction string. We'll have to
parse the text string into a series of matchables, then compare those
against the stream of results we get back from the `instructions()` of the
CodeObject. Parsing the text is a great place to let a regex do most of our
work for us. ::

    import re

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

A Bug is Discovered
~~~~~~~~~~~~~~~~~~~

Running this code produces one surprising result::

    import bytecode

    def main():
        co = bytecode.CodeObject()
        co.append('LOAD_CONST', 42)
        co.append('RETURN_VALUE')
        asm = """
            LOAD_CONST 1 (42)
            RETURN_VALUE
        """
        print(bytecode.instructions_match(co, asm))

    if __name__ == '__main__':
        main()

I got this::

    Traceback (most recent call last):
      File "./test.py", line 36, in <module>
        main()
      File "./test.py", line 32, in main
        print(bytecode.instructions_match(co, asm))
      File "/Users/austin/git/lbac/ch03/bytecode.py", line 296, in instructions_match
        assert_match(match['argindex'], argindex, 'argindex', line)
      File "/Users/austin/git/lbac/ch03/bytecode.py", line 278, in assert_match
        % (field, line, wanted, got))
    ValueError: Mismatch in 'argindex' at line 'LOAD_CONST 1 (42)': 1 != 0

The problem is the 'LOAD_CONST' argument index. According to the output, we are
asking for index # 1, but the system is returning index # 0. What gives?

In fact, if I start up Python and try typing in our favorite function, I get a
similar behavior. ::

    Python 3.3.0 (default, Nov 23 2012, 10:26:01)
    [GCC 4.2.1 Compatible Apple Clang 4.1 ((tags/Apple/clang-421.11.66))] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>> def f():
    ...     return 42
    ...
    >>> f.__code__.co_consts
    (None, 42)

It appears that the [0] slot in the `.co_consts` tuple is always a None value.
This is confirmed when we try an even smaller function definition::

    >>> def g():
    ...     pass
    ...
    >>> g.__code__.co_consts
    (None,)

This is a pretty easy fix. We'll just change the `__init__` code for the
CodeObject class. But this is exactly the sort of "learning about the
environment" I warned you about, before. Every architecture, no matter how
well designed, is going to have these little quirks. When you're writing a
compiler, you need to expect them. Seek them out, and try to get some benefit
out of them  -- presumably they were put in for a reason. ::

    >>> attrs=[x for x in dir(g.__code__) if not x.startswith('_')]
    >>> [ (x, getattr(g.__code__, x)) for x in attrs]
    [('co_argcount', 0), ('co_cellvars', ()), ('co_code', b'd\x00\x00S'),
    ('co_consts', (None,)), ('co_filename', '<stdin>'), ('co_firstlineno', 1),
    ('co_flags', 67), ('co_freevars', ()), ('co_kwonlyargcount', 0),
    ('co_lnotab', b'\x00\x01'), ('co_name', 'g'), ('co_names', ()),
    ('co_nlocals', 0), ('co_stacksize', 1), ('co_varnames', ())]

I have no idea what '67' means for the flags. Presumably we'll find out as
we go along. The various fields being set to 0 or () make sense. The
co_stacksize setting of 1 doesn't make sense, until you realize that the
`pass` statement expands into `return None`.

Changing the `__init__` function to use `[None]` as the initial value for
`co_consts` causes our test case to work, though. So I think we can proceed.

Writing More Test Cases
-----------------------

Now that we have a working framework for writing and passing test cases,
let's write some expressions and try to predict how they will be coded.
We'll have to use input parameters when we deal with the Python compiler,
because it automatically replaces constant expressions with their result.
What's worse, Python apparently optimizes *after* it addes the constants to
the `.co_consts` table::

    >>> def f():
    ...     return 8/2+3*4-6/1
    ...
    >>> f.__code__.co_consts
    (None, 8, 2, 3, 4, 6, 1, 4.0, 12, 16.0, 6.0, 10.0)
    >>> da(f)
      2           0 LOAD_CONST              11 (10.0)
                  3 RETURN_VALUE

From this, we're learning that the constants table will contain a mix of
constants and possibly interim results. Yikes! That makes predicting the
`argindex` a little challenging. (Good thing we don't have to specify it!)

So let's use parameters, instead of constants. That way we'll force the
Python compiler to generate the various operations, instead of just the
interim results::

    >>> def f(a,b,c,d):
    ...     return a*b-c/d
    ...
    >>> da(f)
      2           0 LOAD_FAST                0 (a)
                  3 LOAD_FAST                1 (b)
                  6 BINARY_MULTIPLY
                  7 LOAD_FAST                2 (c)
                 10 LOAD_FAST                3 (d)
                 13 BINARY_TRUE_DIVIDE
                 14 BINARY_SUBTRACT
                 15 RETURN_VALUE

Can we use this for a test case? Sure! Let's give it a try::

    >>> from ch03 import bytecode
    >>> co = bytecode.CodeObject(f)
    >>> expected = """
    ...   2           0 LOAD_FAST                0 (a)
    ...               3 LOAD_FAST                1 (b)
    ...               6 BINARY_MULTIPLY
    ...               7 LOAD_FAST                2 (c)
    ...              10 LOAD_FAST                3 (d)
    ...              13 BINARY_TRUE_DIVIDE
    ...              14 BINARY_SUBTRACT
    ...              15 RETURN_VALUE
    ... """
    >>> bytecode.instructions_match(co, expected)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/Users/austin/git/lbac/ch03/bytecode.py", line 291, in instructions_match
        = next(instr)
      File "/Users/austin/git/lbac/ch03/bytecode.py", line 256, in instructions
        tpl = meth(opnum, it, offset, extended_arg)
      File "/Users/austin/git/lbac/ch03/bytecode.py", line 213, in _decode_opcode_localvar
        raise NotImplementedError("not yet")
    NotImplementedError: not yet

Oh, no! An exception! But wait. It's a "not implemented yet" exception!  Our
code is working fine  -- we just haven't written enough of it. In particular,
the `_decode_opcode_localvar` subroutine is a stub. Let's have a look at
that::

    >>> import opcode
    >>> [ x for x in opcode.haslocal]
    [124, 125, 126]
    >>> [ opcode.opname[x] for x in opcode.haslocal]
    ['LOAD_FAST', 'STORE_FAST', 'DELETE_FAST']

So we're missing three opcodes, and one of them  -- `LOAD_FAST` is used
a lot in our function. Checking the Python documentation [#loadfast]_ we find this
description:

    *LOAD_FAST(var_num)*
        Pushes a reference to the local `co_varnames[var_num]` onto the stack.

So let's add that to our code::

    def _decode_opcode_localvar(self, opnum, it, offset, extended_arg):
        """Return a tuple of (lineno, offset, (labels), opnum, opname,
        argindex, argvalue)."""
        lineno, labels, opname = self._decode_common(opnum, offset)
        argindex = self._decode_argindex(it, extended_arg)
        argvalue = self.co_varnames[argindex]
        return (lineno, offset, labels, opnum, opname, argindex, argvalue)

A Bug is Found
~~~~~~~~~~~~~~

With that change, I get a new failure::

    >>> bc.instructions_match(co, expected)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/Users/austin/git/lbac/ch03/bytecode.py", line 298, in instructions_match
        assert_match(int(match['offset']), offset, 'offset', line)
      File "/Users/austin/git/lbac/ch03/bytecode.py", line 282, in assert_match
        % (field, line, wanted, got))
    ValueError: Mismatch in 'offset' at line '2           0 LOAD_FAST                0 (a)': 0 != 1

Apparently, there's some kind of off-by-one error in our offset handling.
And sure enough, here it is::

    def instructions(self):
        it = iter(self.co_code)
        offset = 0
        extended_arg = None
        while True:
            opnum = next(it)
            offset += 1
            meth = self._decode_dispatch[opnum].__get__(self)
            tpl = meth(opnum, it, offset, extended_arg)
            if tpl[3] == opcode.EXTENDED_ARG:
                extended_arg = tpl[5]
            else:
                extended_arg = None
            yield tpl

Looking hard at the code, I can see where I incremented `offset.` And two
lines later, I see where I use it. Let's just move the increment down after
the fall to `meth()` and try again::

    >>> bc.instructions_match(co, expected)
    True

At Last!
--------

I'm going to draw this chapter to a close. You know that there are a bunch
of not-implemented-yet methods waiting in our code. You also know that our
code is clean enough that filling in those methods will be straightforward.
When we stumble upon an unimplemented method from here on, we can just fill
it in and keep coding.

Presently, our bytecode module handles function parameters (which is more
than our parser does!) and all of the no-argument opcodes. Because the
Python VM is stack based, all the math operations are no-argument opcodes.
They assume that their operands are already on the stack, and they leave
their results on the stack. Just a little bit of coding here has carried us
a long way!

.. rubric:: Footnotes

.. [#innards] http://tech.blog.aknin.name/2010/04/02/pythons-innards-introduction/
.. [#loadfast] http://docs.python.org/3/library/dis.html#opcode-LOAD_FAST
