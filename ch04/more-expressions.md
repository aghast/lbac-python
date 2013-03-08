---
modeline: " vim: set et sts=4 sw=4 ts=4 tw=76: "
layout: chapter
title: More Expressions
---

More Expressions
================

Now, let's see what our bytecode module can do! In this chapter, we'll be
integrating our bytecode module with the expression parser, and then
extending our parser to add more capabilities.

Generating Bytecode
-------------------

To get started, let's recap the capabilities that our expression parser
had at the end of chapter 2. We could:

- recognize numbers;
- handle unary '+' and '-' operators;
- add, subtract, multiply, and divide two operands;
- correctly handle operator precedence;
- handle nested sub-expressions in parentheses.

How will we integrate bytecode? First, our use of literal numbers to
evaluate expressions will change into adding constants to the constants
table (handled already by the bytecode library). The unary '+' operator can
be ignored, and the unary '-' will convert into a dedicated 'UNARY\_NEGATIVE'
opcode. The binary operators all have dedicated opcodes in the Python VM, so
those will convert into dedicated opcodes.  Operator precedence is already
handled by the order in which the parser evaluates the operators. And
parentheses are handled in the same way - by recursively evaluating the
nested sub-expression before the outer expression is evaluated.

All in all, it looks like we have a few cases down at the lower levels of
the parser - the operators, numbers - where we will have to generate
bytecode. And the rest of our features are actually handled implicitly by
the expression parser, so we won't have to make any changes to keep them!

Before we start converting our code to write bytes, let's look at two
issues that may not be clear to you: why does our parser just
'magically' support the correct order of evaluation, and why are
dedicated opcodes significant?

Order of Evaluation
-------------------

Just exactly how does our parser manage to get the order of evaluation
correct? Because we told it to!

If you remember, when we first started parsing expressions, we wrote
code to emulate a four-function calculator. That code just evaluated
expressions in the order they appeared. 3 + 4 \* 5 was evaluated as
(3+4=7) and then (7\*5=35). That, we decided, was wrong.

So we changed our code to use "recursive descent." In this case, the
expression evaluation code for the additive operators (plus and minus)
knew (because we programmed it to know!) that multiplication and
dividion (and other stuff) had a higher precedence than the additive
operators. So before the additive expression code processes anything, it
calls the multiplicative part of the parser to check for
higher-precedence ops. And the multiplicative part, before it does
anything, calls the atom part to check for parens, etc.

In this way, we have coded the parser to implicitly *know* what the
precedence of the operators is, and to automatically implement the
correct order of evaluation. If we generate the code to evaluate our
expressions in the same order we have been computing the results, then
whatever code we generate should also compute correct results, since it
will model its order of evaluation on the order we are using!

Dedicated Opcodes
-----------------

Believe it or not, having dedicated opcodes to support things like
multiplication is a relatively recent thing. In the 1990's, the SPARC
processor (from Sun Microsystems) was shipped with no multiply or divide
instruction in hardware. Instead, the reference manual included software
routines that could be used to perform arbitrary integer multiply and divide
operations using *multiply step* and *divide step* operations built into the
CPU.

Below is the shortest such routine, for unsigned integer multiplication
(multiply two 32-bit numbers into a 64-bit result). Two things you need to
know about the SPARC to have any hope of understanding this code are (1) the
SPARC executes one additional operation during the "branch delay" while the
processor is waiting for a branch target to be fetched, so the next op after
a branch or return statement will be executed always; and (2) the SPARC
processors had a model of three groups of registers that would be shifted
slightly on each subroutine call, so that the %o registers mentioned below
are all visible to the caller on return.:

```gas
/*
 * Procedure to perform a 32 by 32 unsigned multiply.
 * Pass the multiplier in %o0, and the multiplicand in %o1.
 * The least significant 32 bits of the result will be returned in %o0,
 * and the most significant in %o1. *
 * This code has an optimization built-in for short (less than 13 bit)
 * multiplies. Short multiplies require 25 instruction cycles, and long ones
 * require 46 or 48 instruction cycles.
 *
 * This code indicates that overflow has occurred, by leaving the Z condition
 * code clear. The following call sequence would be used if you wish to
 * deal with overflow:
 *
 * call         .umul
 * nop                          ! (or set up last parameter here)
 * bnz          overflow_code   ! (or tnz to overflow handler)
 *
 * Note that this is a leaf routine; i.e. it calls no other routines and does
 * all of its work in the out registers. Thus, the usual SAVE and RESTORE
 * instructions are not needed.
 */
    global      .umul
.umul:
    or          %o0, %o1, %o4   ! logical or of multiplier and multiplicand
    mov         %o0, %y         ! multiplier to Y register
    andncc      %o4, 0xfff, %o5 ! mask out lower 12 bits
    be          mul_shortway    ! can do it the short way
    andcc       %g0, %g0, %o4   ! zero the partial product and clear N and V conditions
    !
    ! long multiply
    !
    mulscc      %o4, %o1, %o4   ! first iteration of 33
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4   ! 32nd iteration
    mulscc      %o4, %g0, %o4   ! last iteration only shifts
/*
 * Normally, with the shift and add approach, if both numbers are
 * nonnegative, you get the correct result. With 32-bit twos-complement
 * numbers, -x can be represented as ((2 - (x/(2**32))) mod 2) * 2**32.
 * To avoid a lot of 2**32’s, we can just move the radix point up to be
 * just to the left of the sign bit. So:
 *
 *  x *  y = (xy) mod 2
 * -x *  y = (2 - x) mod 2 * y = (2y - xy) mod 2
 *  x * -y = x * (2 - y) mod 2 = (2x - xy) mod 2
 * -x * -y = (2 - x) * (2 - y) = (4 - 2x - 2y + xy) mod 2
 *
 * For signed multiplies, we subtract (2**32) * x from the partial
 * product to fix this problem for negative multipliers (see .mul in
 * Section 1.
 * Because of the way the shift into the partial product is calculated
 * (N xor V), this term is automatically removed for the multiplicand,
 * so we don't have to adjust.
 *
 * But for unsigned multiplies, the high order bit wasn't a sign bit,
 * and the correction is wrong. So for unsigned multiplies where the
 * high order bit is one, we end up with xy - (2**32) * y. To fix it,
 * we add y * (2**32).
 */
    tst         %o1
    bge         lf
    nop
    add         %o4, %o0, %o4
1:
    rd          %y, %o0         ! return least sig. bits of prod
    retl                        ! leaf-routine return
    addcc       %o4, %g0, %o1   ! delay slot; return high bits and set
                                ! zero bit appropriately
    !
    ! short multiply
    !
mul_shortway:
    mulscc      %o4, %o1, %o4   ! first iteration of 13
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4
    mulscc      %o4, %o1, %o4   ! 12th iteration
    mulscc      %o4, %g0, %o4   ! last iteration only shifts

    rd          %y, %o5
    sll         %o4, 12, %o4    ! left shift partial product by 12 bits
    srl         %o5, 20, %o5    ! right shift product by 20 bits
    or          %o5, %o4, %o0   ! merge for true product
    !
    ! The delay instruction (addcc) moves zero into %o1,
    ! sets the zero condition code, and clears the other conditions.
    ! This is the equivalent result to a long umultiply which doesn't overflow.
    !
    retl                        ! leaf routine return
    addcc       %g0, %g0, %o1
```

For more information on the SPARC architecture, see [The SPARC
Architecture Manual](http://www.sparc.com/standards/V8.pdf).

The point of this is not for you to learn SPARC assembly, but to
demonstrate that even 'modern' computers may have different levels of
support for some operations than you expect. The Python VM provides a
single opcode to perform a multiply. But that opcode probably performs
an integer (or long) multiply behind the scenes, and *that* may in turn
wind up executing the routine above, if you happen to be on an old,
SPARC-based computer.

If you wind up writing a compiler for some target other than the Python
VM, you will need to concern yourself with this stuff. On modern
(superscalar) CPUs that include a MUL instruction, it will typically
take 10 cycles, give or take 10. (Yes, it is possible to get a 0-cycle
multiply. You need a deep pipeline, or a cache miss.) One of the reasons
I like writing for the Python VM is that I can gloss over all these
issues. :-)

Generating Bytecode
-------------------

With those questions answered, let's get on with generating bytecode!
We'll start with a copy of the cradle from chapter 2, and a copy of the
bytecode module from chapter 3. The first thing we'll have to change - and
yes, this change will be to the cradle.py file - will be the behavior of the
emit and emitln functions. First, because there is no emitln when generating
bytecode, and second because we will be writing to a code object, not to a
file.

How should we test our code? In chapter 3 we created a CodeObject, then
called the ``instruction_match()`` method on the object. I think that's a
reasonable place for us to start, except that we can let the compile
method return the code object. (Surprise! This is one of the behaviors
of Python's built-in compile function, too.)

Thus, a test case will look something like this:

```
def test_something(self):
    ... setup ...
    co = compiler.compile(...)
    asm = """ some assembly code """
    instructions_match(co, asm)
```

Let's go ahead and write the first test case and store it into
`tests/expr1_tests.py`. We'll extract the setup and test code into an
`assertExpr()`: subroutine, to make writing test cases easy:

```
from io import StringIO
import unittest

from ch04.bytecode import instructions_match
from ch04 import expr1 as compiler

class TestCompiler(unittest.TestCase):

    def assertExpr(self, text, asm):
        compiler.init(inp=StringIO(text))
        co = compiler.compile()
        instructions_match(co, asm)

    def test_constant(self):
        asm = """
            LOAD_CONST 1 (7)
            RETURN_VALUE
        """
        self.assertExpr("7", asm)
```

Run the tests, and guess what? Nothing works. Well, let's get to solving
the problems. First, let's implement an emit routine that uses a code object. This goes in cradle.py.

```
    def emit(op, arg=None):
        _Code.append(op, arg)
```

Well, that was easy. But we'll have to add the module variable \_Code,
and some code in the init function to support it. Here's my version. Notice
that I've removed the _Output variable in favor of _Code:

```
##### Output functions

_Code = None
""" CodeObject for compiled results. """

def emit(op, arg=None):
    _Code.append(op, arg)

##### Processing

def init(inp=None, out=None, err=None):
    global _Code, _Input, _Error
    _Error = err if err is not None else sys.stderr
    _Input = inp if inp is not None else _Input
    # 'prime the pump' to read first character, etc.
    get_char()
    _Code = bytecode.CodeObject()
```

With that out of the way, let's implement a dumb expression parser that
only recognizes a single number. First, copy the cradle over to a new file.
Mine is called expr1.py. You'll remember that this is how we got
started, so it should be easy:

```
def compile():
    expression()
    return _Code

def expression():
    num = int(get_number())
    emit('LOAD_CONST', num)
    emit('RETURN_VALUE')
```

Well, that seemed to work. But of course, it's not very challenging.  Let's
go to a mixed model that can support additive operators or a single value:

```
def expression():
    expr_addop()

def expr_addop():
    expr_atom()
    if Peek == '+':
        expr_add()
    elif Peek == '-':
        expr_subtract()

def expr_atom():
    if Peek.isdigit():
        atom = int(get_number())
        emit('LOAD_CONST', atom)
    else:
        expected('Atom')

def expr_add():
    match('+')
    # WHAT GOES HERE?
```

And here we run into a problem in the ``expr\_add`` function. With the "do
it now!" model that we were using in chapter 2, we passed around the
intermediate results as parameters to the various functions. If you'll
recall, the ``expr\_addop`` code from chapter 2 looked like this:

```
def expr_addop():
    result = expr_mulop()
    while Peek is not None and Peek in "+-":
        if Peek == "+":
            result = expr_add(result)
        elif Peek == "-":
            result = expr_subtract(result)
    return result
```

The expr\_mulop code computed a multiplication, or possibly just
returned an atom. Then if an addop was present, the initial value
(result) was passed in to the add or subtract code, and a new result was
computed, until eventually there were no more addops. Then the final
result was returned.

How are we going to pass the result around when we don't actually have
the result? The result, like everything else, has to be managed in the
bytecode we are writing!

Register Management
-------------------

Ironically, we're talking about **register management,** on a machine that
has no registers. But that's okay, because if there *were* some registers,
we would need to manage them, and we'd be having the same conversation at
the same place.

Sometimes this is referred to as the **calling convention(s)** or as the
**ABI** (application binary interface). But regardless, there are some
questions that have to be answered, and this is the place to do it.

On the Intel x86 platform, for example, there are registers. And certain
opcodes, like MUL, use both the AX and DX registers to hold their
results. So you can't leave any value that you need to keep in the DX
register while doing a multiply. This begs the question, are there any
registers that should always be saved? Who should save them - the
caller, or the callee?

It doesn't matter to us, because the answers are all the same: the
Python VM has no registers, so everything has to go on the stack. But
when you are writing a compiler for a different system, you will have to
know what the questions are, and you will have to know the answers, too!

Anyway, here are some questions. See if you can figure out the answers.
(Hint: look up!)

1.  Q: How can we hold a number that we compute with expr\_atom?

    A: "the Python VM has no registers, so everything has to go on the
    stack."

2.  Q: How can we store a number temporarily, so that a following ADD
    or SUBTRACT operation can find it?

    A: \_\_\_\_\_\_

3.  Q: How can we store the arguments to a MULTIPLY or DIVIDE
    operation?

    A: \_\_\_\_\_\_

4.  Q: What about unary operations? How can we set up a number for
    those?

    A: \_\_\_\_\_\_

So, how did you do? I hope you got all the answers right. And I
certainly hope all your answers were the same. Because this is how we
manage the values we want to pass around in the Python VM: they go on
the stack!

If we are going to do an add of two numbers, we set it up by putting the
first number on the stack, then putting the second number on the stack, and
then doing a BINARY\_ADD, which takes (pops) two numbers off the stack, and
puts (pushes) their sum on the stack.

What we need to do, then, is to trust that all the steps before us have
configured the stack the way it needs to be configured. Thus, if the add
and subtract (and multiply, divide, modulus, ...) operators need a left
operand to be on the stack, we just assume that it's there. (And write
lots of test cases to make *damn sure* that we're right!) Let's give it
a try:

```
def expr_add():
    # Assume first addend is already on stack.
    match('+')
    expr_atom() # Read second addend, put on stack.
    emit('BINARY_ADD')
```

And that's it! As long as we write all the other code correctly, to
leave their results on the stack, we can assume that the incoming
parameter is on the stack, and then add the numbers we need to add, and
leave our own results on the stack.

Let's catch up on our test cases, and then go a little bit farther. Add
test cases for all four basic operations, plus some test cases for
operator precedence. (Feel free to copy them from the tests we wrote in
chapter 2!) Here are mine:

```
def test_add(self):
    asm = """
        LOAD_CONST 1 (1)
        LOAD_CONST 2 (8)
        BINARY_ADD
        RETURN_VALUE
    """
    self.assertExpr("1+8", asm)

def test_subtract(self):
    asm = """
        LOAD_CONST 1 (8)
        LOAD_CONST 2 (3)
        BINARY_SUBTRACT
        RETURN_VALUE
    """
    self.assertExpr("8-3", asm)

def test_multiply(self):
    asm = """
        LOAD_CONST 1 (3)
        LOAD_CONST 2 (2)
        BINARY_MULTIPLY
        RETURN_VALUE
    """
    self.assertExpr("3*2", asm)

def test_divide(self):
    asm = """
        LOAD_CONST 1 (3)
        LOAD_CONST 2 (2)
        BINARY_FLOOR_DIVIDE
        RETURN_VALUE
    """
    self.assertExpr("3/2", asm)
```

The only tricky part is the opcode for division. Remember that I want
all our expressions to use integer values, so we need to use the FLOOR
instead of the TRUE division opcode.

The code itself should be a snap, now. The precedence implementation is
the same - add and subtract call mulop, multiply and divide call atom.
If you have trouble, refer back to chapter 2.

Once you have that working, let's add support for parentheses and multiple
operators (if you didn't add them before). Again, we can take the test cases
from chapter 2. Pay careful attention to the opcodes in
test\_multiple\_binops, below. You have to understand how the additive and
multiplicative precedence levels are working together to predict how the
opcodes will be generated. Remember that mulop is basically "greedy," while
addop is basically "lazy." This means that we interrupt the addop to insert
a multiply, and a divide. That leaves the first argument (1) on the stack.
It may seem strange, but we're counting on all the intervening processing to
just leave our value alone on the stack until we get back to it. And it
works!:

```
def test_multiple_binops(self):
    asm = """
        LOAD_CONST 1 (1)
        LOAD_CONST 2 (2)
        LOAD_CONST 3 (4)
        BINARY_MULTIPLY
        LOAD_CONST 4 (3)
        BINARY_FLOOR_DIVIDE
        BINARY_ADD
        RETURN_VALUE
    """
    self.assertExpr("1+2*4/3", asm)

def test_paren_expr(self):
    asm = """
        LOAD_CONST 1 (1)
        LOAD_CONST 2 (2)
        BINARY_ADD
        LOAD_CONST 3 (3)
        LOAD_CONST 4 (4)
        BINARY_ADD
        BINARY_MULTIPLY
        RETURN_VALUE
    """
    self.assertExpr("(1+2)*(3+4)", asm)
```

Another Bug is Found
--------------------

I made my ``expr_atom`` function recurse by calling expression. (As opposed
to calling ``expr_addop.)`` And when I ran the ``test_paren_expr`` test, I
discovered a bug: the ``expression`` function automatically appends a
'RETURN\_VALUE' opcode when it finishes. Oops! That will have to be moved to
``compile,`` instead. This is what the 'calling conventions' mean: that
function was expected to return a value. Returning a value means leaving it
on the stack. Some other piece of code has to take the value off the stack.
With that change, everything works.

Unary Precedence
----------------

I promised in chapter 2 that I would re-visit the issue of unary
operator precedence. Before we start working on adding unary operators
to our code, let's do that.

Most programming languages, inspired by the C/Algol family tree, accept
unary operators at pretty much any location. You can negate any single
term just by putting a '-' in front of it.

But there are a lot of mathematicians who feel that this is pointless.
If you need to subtract a number, just subtract it! Don't bother with
adding the negative. They feel that "a - b" is easier to read, and more
sensible, than "a + -b" or "-b + a".

In this case, why not move the unary from the highest precedence to the
lowestr?. Instead of allowing a negative sign in front of every term, why
not allow at most one negative sign, right at the front of an expression.
Everything else can be handled by changing add to subtract, or
subtract to add, or by wrapping parens around a sub-expression.

My own, personal, bias is to make my expression parser act like C. But
if you're more mathematically inclined, maybe you want to speed things
up by eliminating all the unary minuses except one. That would change the
``expression`` code to something like:

```
def expression():
    if Peek == '-':
        negated = true
        match('-')
    else:
        negated = false

    # ... regular stuff goes here ...

    if negated:
        emit('UNARY_NEGATE')
```

I'm not going to do that. I'm a stodgy old C programmer at heart, so I'm
going to follow the same path we followed back in chapter 2, and insert
unary operators just below ``expr_atom`` in the precedence hierarchy:

```
def expr_unary():
    if Peek is None:
        expected('UnaryOp or Atom')
    if Peek in "+-":
        if Peek == "+":
            expr_unary_plus()
        elif Peek == "-":
            expr_unary_minus()
        else:
            expected('UnaryOp')
    else:
        expr_atom()

def expr_unary_plus():
    match('+')
    expr_atom()

def expr_unary_minus():
    match('-')
    expr_atom()
    emit('UNARY_NEGATIVE')
```

All the references to ``expr_atom()`` in the multiple, divide, etc.,
handlers will have to change to refer to ``expr_unary().`` The test cases
are simple:

```
def test_unary_minus(self):
    asm = """
        LOAD_CONST 1 (3)
        UNARY_NEGATIVE
    """
    self.assertExpr("-3", asm)

def test_unary_plus(self):
    asm = """
        LOAD_CONST 1 (8)
        RETURN_VALUE
    """
    self.assertExpr("+8", asm)
```

Great! Now we have a bytecode-generating version of our parser from chapter
2. This is a great stopping point. If you've got things to do, now would be
a good time to take a break.

Variables
=========

We have an expression compiler that right now only supports constant
expressions. The obvious next thing to add would be variables. With
variables, we can build a desktop calculator to match the best of them! And
also, we'll be on our way to loops and subroutines.

Let's start off by seeing how Python does it. We'll feed the Python compiler
three different kinds of symbols: paramters, local variables, and global
variables.

```
>>> def f(x):
...     y = x+1
...     global g
...     g = y+x
...     return g
...
>>> dis.dis(f)
  2           0 LOAD_FAST                0 (x)
              3 LOAD_CONST               1 (1)
              6 BINARY_ADD
              7 STORE_FAST               1 (y)

  4          10 LOAD_FAST                1 (y)
             13 LOAD_FAST                0 (x)
             16 BINARY_ADD
             17 STORE_GLOBAL             0 (g)

  5          20 LOAD_GLOBAL              0 (g)
             23 RETURN_VALUE
```

What we can see is that Python treats accesses to parameters and accesses to
local variables the same - it uses the same opcode, `LOAD_FAST,` for both
parameter 'x' and local variable 'y'. (That's _definitely_ not true in other
environments.) And global variables are accessed using the `LOAD_GLOBAL` and
`STORE_GLOBAL` instructions, instead of the ...\_FAST ones.

That seems pretty straightforward. Now we just have to make sure we keep our
variables numbered correctly. The append logic in bytecode should handle
this, except that we haven't written it yet. So I guess that's what we
should do first. Here are the specifications for the LOAD_FAST and
LOAD_GLOBAL opcodes, from the =dis= module page:

    LOAD_FAST(var_num)
        Pushes a reference to the local co_varnames[var_num] onto the stack.

    LOAD_GLOBAL(namei)
        Loads the global named co_names[namei] onto the stack.

Having identified which list of names we should search, let's get coding!

```
def _append_opcode_localvar(self, opnum, arg):
    value_list = self.co_varnames
    try:
        arg_index = value_list.index(arg)
    except ValueError:
        arg_index = len(value_list)
        value_list.append(arg)
    self.append_bytecode(opnum, arg_index)

def _append_opcode_name(self, opnum, arg):
    value_list = self.co_names
    try:
        arg_index = value_list.index(arg)
    except ValueError:
        arg_index = len(value_list)
        value_list.append(arg)
    self.append_bytecode(opnum, arg_index)
```

That should take care of both the ...\_FAST and the ...\_GLOBAL instructions
for variable load and store. Now let's refactor the common code into a
helper method, and fix up the constant handler already in bytecode.py.

```
def _append_table_helper(self, opnum, arg, table):
    try:
        arg_index = table.index(arg)
    except ValueERror:
        arg_index = len(table)
        table.append(arg)
    self.append_bytecode(opnum, arg_index)

def _append_opcode_localvar(self, opnum, arg):
    self._append_table_helper(opnum, arg, self.co_varnames)

def _append_opcode_name(self, opnum, arg):
    self._append_table_helper(opnum, arg, self.co_names)

def _append_opcode_const(self, opnum, arg):
    self._append_opcode_const(self, opnum, arg, self.co_consts)
```

With that fixed, let's talk about how we should do variables in expressions.
I think we'll stick to global variables, at first, so we can use them
without having to deal with assignment statements. When we parse variables
in an expression, they are going to be read-only. We'll deal with assignment
later.

No assignments means that any reference we make to a variable is a read.
That lets us write a function like expr_read_var. The function will take a
name, and emit a reference that loads the name into the stack.

```
def expr_read_var():
    varname = get_identifier()
    emit('LOAD_GLOBAL', varname)
```

We can integrate this into the `expr_atom` function:
```
def expr_atom(self):
    if Peek == '(':
        match('(')
        expression()
        match(')')
    elif Peek.isalpha():
        expr_read_var()
    else:
        num = int(get_number())
        emit('LOAD_CONST', num)
```
Don't forget the test cases:
```
def test_read_variable(self):
    asm = """
        LOAD_FAST 0 (a)
        RETURN_VALUE
    """
    self.assertExpr("a", asm)

def test_read_2_variables(self):
    asm = """
        LOAD_FAST (a)
        LOAD_CONST (1)
        BINARY_ADD
        LOAD_FAST (b)
        LOAD_CONST (2)
        BINARY_ADD
        BINARY_MULTIPLY
        RETURN_VALUE
    """
    self.assertExpr("(a+1)*(b+2)", asm)
```
That is GREAT! That was pretty easy to code, and the test cases passed as
soon as I got a typo fixed. I'm feeling so good about how that went, that
I'm tempted to add some more capability. Let's add global symbols! We'll
need to be able to differentiate between global and local variables, but
that should be pretty easy. Here's a simple implementation:
```
def is_global(name):
    return False

def expr_read_var():
    varname = get_identifier()
    if is_global(varname):
        emit('LOAD_GLOBAL', varname)
    else:
        emit('LOAD_FAST', varname)
```
That's kind of funny. But C already has a protocol for local versus global
variables: first letter upper-case. Since our variables are only one letter
long, we can still get away with it.
```
def is_global(name):
    return name[0].isupper()
```
Well, it _almost_ works:
```
  File "/Users/austin/git/lbac/ch04/bytecode.py", line 242, in
_decode_opcode_name
    raise NotImplementedError("not yet")
NotImplementedError: not yet
```
Apparently, when we add something to the _encoder,_ we have to add it to the
_decoder,_ as well! A quick fix...
```
def _decode_opcode_name(self, opnum, it, offset, extended_arg):
    """Return a tuple of (lineno, offset, (labels), opnum, opname,
    argindex, argvalue)."""
    lineno, labels, opname = self._decode_common(opnum, offset)
    argindex = self._decode_argindex(it, extended_arg)
    argvalue = self.co_names[argindex]
    return (lineno, offset, labels, opnum, opname, argindex, argvalue)
```

... and we're ready to try again! That is another one of those
copy-and-paste functions. Only the ``co_names`` is any different.  That gets
the test cases to pass. Let's try something fun in the Python interpreter:

```
>>> from ch04 import expr1
>>> from io import StringIO as sio
>>> expr1.init(inp=sio("A+1"))
>>> co = expr1.compile()
>>> A = 1234
>>> fn = co.to_function(globals())
>>> fn()
1235
```

_How about that?_

I don't think anyone can argue with that result. Our "toy compiler" parses
an arithmetic expression, generates a set of Python bytecode, and with one
more method call, we can integrate our compiled code with Python code. At
this point, you have a simple, but full-fledged, compiler. There are no
tricks. We are processing the input, parsing the expression, writing the
bytecodes- it's a compiler!

Assignments
===========

Flush with that success, let's ask the obvious question: what do we have to
do in order to store values into variables? How do we code an assignment?

First, though, we need to think about one of the differences between C and
Python. In C, the assignment operators (all those operators like += and -=
are included in the list) are _operators._ In C, you can use assignment
anywhere you could use another operator, like addition. That means that this
code is valid C:
```C
while (*dst++=*src++)
    /* empty --> */ ;
```
Python, on the other hand, defines an _assignment statement_ that has a
chained syntax very much like that of C. But assignment is not an operator,
and cannot appear in the middle of an expression.

This is a Python design decision. And like a lot of Python's design
decisions, it is somewhat controversial. But many other languages before C
also treated assignment as a statement rather than an operator. So this is
one of those decisions you will have to make: is assignment a statement type
or a binary operator?

For this exercise, I'm going to treat it as a statement. We've been
processing expressions from the beginning - I think it's time to branch out
a little bit!

One problem with assignment statements, though, is that they lead to other
kinds of statements. Up until now, our expressions have been pure
expressions, whose value could simply be evaluated and returned to the
caller. When we add assignment statements to the mix, it leads to wanting to
evaluate other expressions in the context of the assignments:
```
x=1
y=2
z=x+y
```
And that leads to grouping statements together. The next thing you know,
we'll be adding curly braces!

Let us add a new rule to our language. So far, all our expressions have fit
on one line, and I don't see a reason to change that. Even Python has a way
to separate one statement from another on the same line: the semicolon. So
we will accept one or more _statements,_ with the statements separated by
semicolon characters. For example: ``a=1;b=2;c=a+b*3``

Change the Filename!
--------------------
This is a significant change. And so before we do anything else, we should
make a copy of our code. I'll copy my `expr1.py` code over to `expr2.py` and
carry on from there. Obviously, the test code has to be copied as well.
Sorry for the interruption. Carry on!

How does this affect our grammar? Well, one thing we _don't_ have to worry
about is inserting yet another level of precedence! Instead, we'll be
recognizing two kinds of statement. So let's write a function for that.
```
def statement():
    if Peek.isalpha():
        # ???
    else:
        expression()
```
And...here's a problem. When we are looking at a variable at the beginning
of our "statement," it's ambiguous. It could be the start of an assignment,
like "x=1". But it might also be the start of a simple expression that
happens to use a variable, like "x+3". How can we differentiate these two
cases?

  * One thing we could do is "hoist" the starting tokens up into the
    ``statement`` function. By matching the leading variable-reference and
    then testing for the assignment operator, we could then pass it in to an
    expression or assignment matching function. Yes, this is just as
    horrible an idea as it sounds.

    Our problem is that we don't retain the input. We generate our bytecode
    just as we read it. That is great for speed and simplicity, but not so
    great when we want just a little bit more context to make a decision.

  * We can steal an idea from the Python grammar itself, here, and realize
    that our `expression()` function will stop when it reaches a character
    that it cannot incorporate into an expression. So if we have an input
    like "a=1" and we call `expression`, it will generate the bytecode for
    reading the 'a' variable, and then stop when it sees '=', which is not
    an expected part of an expression.

    We could put in a global boolean that indicated if the 'expression' we
    had seen up to now was a valid _lvalue_ (a value that can appear on the
    left side of an assignment). Then when we saw an assignment operator, we
    would know the left side was legitimate, and could process the
    assignment.

    Of course, there's this code to read the value already generated. Maybe
    we could emit some more code to pop the value off the stack?

  * We could requires a special keyword, or a special name. In Pascal, the
    return value from a function is generated by assigning to a
    "variable" that is the name of the function. Something like this:

        function name_of_the_function;
        begin
            name_of_the_function := 1;
        end

    Or alternatively, we could put a keyword at the beginning of the line.
    That key word would 'predict' for us that this was going to be an
    assignment statement, like 'let':

        let x = 1
        let y = 2

    Alternatively, we could use the keyword for the resulting value, and
    assume that any expression that doesn't have the keyword is an
    assignment:

        x = 1
        y = 2
        return x + y

  * We could _edit_ the bytecode we have generated: in conjunction with the
    `is_lvalue` idea above, we could simply go back and remove the
    bytecode to replace the LOAD with a STORE.

  * We could start building a "tree" while parsing our expressions, and not
    actually generate any bytecode until we had a good idea what was
    happening. This is a good idea, but I'm going to put it off for a bunch
    of chapters.

You've probably figured out that I'm inclined to go with something that
looks like C where possible. So I'm going to ignore the possibilities of the
'let' keyword. Instead, let's adopt the `return` keyword, or `z` for short.
(I want to keep 'r' available for the chapter on loops.)

This means that any statement except the last one should be an assignment.
That will make the coding simpler!
```
def compile():
    while Peek is not None and Peek != 'z':
        stmt_assignment()
        match(';')

    if Peek is None:
        expected('Return Expression')
    stmt_return()
    return _Code

def emit_store_var(varname):
    opcode = 'STORE_GLOBAL' if is_global(varname) else 'STORE_FAST'
    emit(opcode, varname)

def stmt_assignment():
    lvalue = get_identifier()
    match('=')
    expression()
    emit_store_var(lvalue)

def stmt_return():
    match('z')
    expression()
    emit('RETURN_VALUE')
```
Well, _that_ wasn't very hard at all! And it's because we spent a little
time to plan. Trying to implement assignment as an operator would have been
a whole different story with the way our code is currently shaped.

Here are some tests:
```
def test_assignment(self):
    asm = """
        LOAD_CONST (7)
        STORE_FAST (x)
        LOAD_CONST (0)
        RETURN_VALUE
    """
    self.assertExpr("x=7;z0", asm)

def test_return_var(self):
    asm = """
        LOAD_CONST (1)
        STORE_FAST (x)
        LOAD_FAST (x)
        RETURN_VALUE
    """
    self.assertExpr("x=1;zx", asm)
```

Functions
=========

Functions in Python seem like simple things. But there is a pretty wide
amount of variety in how things are handled, depend on context. Let's look
at some examples:

* There are *builtin* functions that call C code directly, instead of
  bytecode.
* Global functions are what most people thing of: a ``def func():`` appears
  somewhere in a module, and it is called in other places.
* Method calls, which look like ``obj.meth(args),`` eventually resolve down
  to function calls.
* Functions can be nested inside classes (see above) or inside other
  functions. Nested functions aren't visible everywhere.
* Functions can also be *closures* if they make reference to a free variable
  that isn't global.
* Functions can be *generators* or *coroutines.*
* Functions can be imported from a different module.

Whew! That's a lot of different things to be hiding behind a set of
parentheses! Let's simplify things as much as we can, and stick to plain old
global-scope bytecode functions. I think it's time to do an experiment with
the Python interpreter:

```
>>> def g():
...     return 1
...
>>> def f():
...     x = g()
...     print("x is: ")
...     print(x)
...
>>> from dis import dis as da
>>> da(f)
  2           0 LOAD_GLOBAL              0 (g)
              3 CALL_FUNCTION            0 (0 positional, 0 keyword pair)
              6 STORE_FAST               0 (x)

  3           9 LOAD_GLOBAL              1 (print)
             12 LOAD_CONST               1 ('x is: ')
             15 CALL_FUNCTION            1 (1 positional, 0 keyword pair)
             18 POP_TOP

  4          19 LOAD_GLOBAL              1 (print)
             22 LOAD_FAST                0 (x)
             25 CALL_FUNCTION            1 (1 positional, 0 keyword pair)
             28 POP_TOP
             29 LOAD_CONST               0 (None)
             32 RETURN_VALUE
```

Looking at the first three lines of the disassembly, we can see the name
lookup, the call, and the assignment of hte result into 'x'. That doesn't
seem too hard for us to model.

Looking further down, we see the call to print with one argument generates a
``LOAD_CONST`` opcode and a ``POP_TOP`` to handle the fact that the return
value is being thrown away. Again, not too much to handle.

What we know so far is that the function being called goes onto the stack
first. Then the arguments go on the stack. We don't know in what order, but
I'm guessing left to right. We'll check in a minute. Then the call is made.

Inside the function, the callee apparently cleans up the stack, or maybe the
call or return opcodes handle that. The callee returns a single value, which
is the result of the function.

Let's look at the order of arguments:

```
>>> def f():
...     g(1,2,3)
...
>>> da(f)
  2           0 LOAD_GLOBAL              0 (g)
              3 LOAD_CONST               1 (1)
              6 LOAD_CONST               2 (2)
              9 LOAD_CONST               3 (3)
             12 CALL_FUNCTION            3 (3 positional, 0 keyword pair)
             15 POP_TOP
             16 LOAD_CONST               0 (None)
             19 RETURN_VALUE
```

Yep, it's left-to-right. The arguments 1,2,3 go on with the leftmost first,
the rightmost last on the stack. Let's look at how we could write the code
to generate this.

First, we would have to recognize a function call. That should be
straight-forward: a name followed by an opening parenthesis like 'f('. When
we see that, we know it's a function call. (As opposed to a paren followed
by a name, like '(f', which is just a nested expression.)

Once we have a parenthesis, we need to match opening and closing parens
until we find our corresponding closing paren. The individual parameter
values will be nested expressions, separated by commas. This should handle
the balancing of parentheses.

Where does a function call fit in the precedence chain? Well, according to C
it is pretty much the highest priority operation. The *postfix* operators,
which includes x++, x--, a[i], and f(x), are higher precedene than the unary
prefix operators. (This makes sense: -f(x) is negating the result of the
call, not calling a negated function.)

We *could* try to follow the C route, of allowing any arithmetic expression
to be treated as a pointer to a function. But I don't think we're ready for
that just yet. So instead, let's admit that a function has a name, and let's
insert function call recognition in with name recognition.

Multi-Character Tokens
======================

White Space
===========
