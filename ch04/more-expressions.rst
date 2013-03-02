.. vim: set et sts=4 tw=4 ts=4 tw=76:
.. Let's Build a Compiler (in Python)! chapter 4 text file.
   Created Thu Feb 21 20:12:41 2013, by austin.

More Expressions
================

Now that we have a bytecode module that somewhat works, let's see what we
can do with it. In this chapter, we'll be integrating our bytecode module
with the expression parser, and then extending expression parsing to add
more capabilities.

Generating Bytecode
-------------------

To start with, let's recap the capabilities that our expression parser had
at the end of chapter 2. We could:

   - recognize numbers;
   - handle unary '+' and '-' operators;
   - add, subtract, multiply, and divide two operands;
   - correctly handle operator precedence;
   - handle nested sub-expressions in parentheses.

Let's look at how we will integrate generating bytecode. First, our use of
literal numbers will convert to adding constants to the constants table
(handled already by the bytecode library). The unary '+' operator can be
ignored, and the unary '-' will convert into a dedicated 'UNARY_NEGATIVE'
opcode. The binary operators all have dedicated opcodes in the Python VM, so
those will convert into dedicated opcodes. Operator precedence is
already handled by the order in which the parser evaluates the operators.
And parentheses are handled in the same way - by recursively evaluating the
nested sub-expression before the outer expression is evaluated.

All in all, it looks like we have a few cases - the operators - where we
will have to generate bytecode. And the rest of our features are actually
handled implicitly by the expression parser, so we won't have to make any
changes to keep them!

Before we start converting our code to write bytes, let's look at two issues
that may not be clear to you: why does our parser just 'magically' support
the correct order of evaluation, and why are dedicated opcodes significant?

Order of Evaluation
~~~~~~~~~~~~~~~~~~~

Just exactly how does our parser manage to get the order of evaluation
correct? Because we told it to!

If you remember, when we first started parsing expressions, we wrote code to
emulate a four-function calculator. That code just evaluated expressions in
the order they appeared. 3 + 4 * 5 was evaluated as (3+4=7) and then
(7*5=35). That, we decided, was wrong.

So we changed our code to use "recursive descent." In this case, the
expression evaluation code for the additive operators (plus and minus) knew
(because we programmed it to know!) that multiplication and dividion (and
other stuff) had a higher precedence than the additive operators. So before
the additive expression code processes anything, it calls the multiplicative
part of the parser to check for higher-precedence ops. And the
multiplicative part, before it does anything, calls the atom part to check
for parens, etc.

In this way, we have coded the parser to implicitly *know* what the
precedence of the operators is, and to automatically implement the correct
order of evaluation. If we generate the code to evaluate our expressions in
the same order we have been computing the results, then whatever code we
generate should also compute correct results, since it will model its order
of evaluation on the order we are using!

Dedicated Opcodes
~~~~~~~~~~~~~~~~~

Believe it or not, having dedicated opcodes to support things like
multiplication is a relatively recent thing. In the 1990's, the SPARC
processor (from Sun microsystems) was shipped with no multiply or divide in
hardware. Instead, the reference manual included software routines that
could be used to perform arbitrary integer multiply and divide operations
using *multiply step* and *divide step* operations built into the CPU.

Below is the shortest such routine, for unsigned integer multiplication
(32x32 bits into 64 bits of output). Two things you need to know about the
SPARC to have any hope of understanding this code are (1) the SPARC executes
one additional operation during the "branch delay" while the processor is
waiting for a branch target to be fetched, so the next op after a branch or
return statement will be executed always; and (2) the SPARC processors had a
model of three groups of registers that would be shifted slightly on each
subroutine call, so that the %o registers mentioned below are all visible to
the caller on return.::

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

For more information on the SPARC architecture, see The SPARC Architecture
Manual. [1]_

  _[1]: http://www.sparc.com/standards/V8.pdf

The point of this is not for you to learn SPARC assembly, but to demonstrate
that even 'modern' computers may have different levels of support for some
operations than you expect. The Python VM provides a single opcode to
perform a multiply. But that opcode probably performs an integer (or long)
multiply behind the scenes, and *that* may in turn wind up executing the
routine above, if you happen to be on a SPARC-based computer.

If you wind up writing a compiler for some target other than the Python VM,
you will need to concern yourself with this stuff. On modern (superscalar)
CPUs that include a MUL instruction, it will typically take 10 cycles, give
or take 10. (Yes, it is possible to get a 0-cycle multiply. You need a deep
pipeline, or a cache miss.) One of the reasons I like writing for the Python
VM is that I can gloss over all these issues. :-)

Generating Bytecode
~~~~~~~~~~~~~~~~~~~

With those questions answered, let's get to coding! We'll start with a copy
of the cradle from chapter 2. The first thing we'll have to change - and
yes, this change will be to the `cradle.py` file - will be the behavior of
the `emit` and `emitln` functions. First, because there is no `emitln` when
generating bytecode, and second because they will write to a code object,
not to an output file.

How should we test our code? In chapter 3 we created a CodeObject, then
called the `check_bytecodes` method on the object. I think that's a
reasonable place for us to start, except that we can let the `compile`
method return the code object. (Surprise! This is one of the behaviors of
Python's built-in `compile` function, too.)

Thus, a test case will look something like this::

    def assertExpr(self, text, asm):
        compiler.init(inp=StringIO(text))
        co = compiler.compile()
        co.check_bytecodes(asm)

    def test_something(self):
        asm = """ some assembly code """
        self.assertExpr("1+2", asm)

Let's go ahead and write the first test case and store it into
`tests/expr1_tests.py`::

    from io import StringIO
    import sys
    import unittest

    from ch04 import expr1 as compiler

    class TestCompiler(unittest.TestCase):

        def assertExpr(self, text, asm):
            compiler.init(inp=StringIO(text))
            co = compiler.compile()
            co.check_bytecodes(asm)

        def test_constant(self):
            asm = """
                LOAD_CONST 1 (7)
                RETURN_VALUE
            """
            self.assertExpr("7", asm)

Run the tests, and guess what? Nothing works. Well, let's get to solving
the problems. First, copy over the cradle code to expr1.py. Next, let's
implement an `emit` routine that uses a code object::

    def emit(op, arg=None):
        _Code.append(op, arg)

Well, that was easy. But we'll have to add the module variable `_Code,` and
some code in the `init` function to support it. Here's my version::

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

With that out of the way, let's implement a dumb expression parser that only
recognizes a single number. You'll remember that this is how we got started,
so it should be easy::

    def compile():
        expression()
        return _Code

    def expression():
        num = int(get_number())
        emit('LOAD_CONST', num)
        emit('RETURN_VALUE')

Well, that seemed to work. But of course, it's not very challenging. Let's
go to a mixed model that can support additive operators or a single value::

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
        # WHAT NOW?

And here we run into a problem in the `expr_add` function. With the "do it
now!" model that we were using in chapter 2, we passed around the
intermediate results as parameters to the various functions. If you'll
recall, the `expr_addop` code from chapter two looked like this::

    def expr_addop():
        result = expr_mulop()
        while Peek is not None and Peek in "+-":
            if Peek == "+":
                result = expr_add(result)
            elif Peek == "-":
                result = expr_subtract(result)
        return result

The `expr_mulop` code computed a multiplication, or possibly just returned
an atom. Then if an addop was present, the initial value (result) was passed
in to the add or subtract code, and a new result was computed, until
eventually there were no more addops. Then the final result was returned.

How are we going to pass the result around when we don't actually have the
result? The result, like everything else, has to be managed in the bytecode
we are writing!

Register Management
~~~~~~~~~~~~~~~~~~~

Ironically, we're talking about **register management,** on a simulated
machine that has no registers. But that's okay, because if there *were* some
registers, we would need to manage them, and we'd be having the same
conversation at the same place.

Sometimes this is referred to as the **calling convention(s)** or as the
**ABI** (application binary interface). But regardless, there are some
questions that have to be answered, and this is the place to do it.

On the Intel x86 platform, for example, there are registers. And certain
opcodes, like MUL, use both the AX and DX registers to hold their results.
So you can't leave any value that you need to keep in the DX register while
doing a multiply. This begs the question, are there any registers that
should always be saved? Who should save them - the caller, or the callee?

It doesn't matter to us, because the answers are all the same: the Python VM
has no registers, so everything has to go on the stack. But when you are
writing a compiler for a different system, you will have to know what the
questions are, and you will have to know the answers, too!

Anyway, here are some questions. See if you can figure out the answers.
(Hint: look up!)

  #. Q: How can we hold a number that we compute with `expr_atom`?
     A: "the Python VM has no registers, so everything has to go on the stack."

  #. Q: How can we store a number temporarily, so that a following ADD or SUBTRACT operation can find it?
     A: ______

  #. Q: How can we store the arguments to a MULTIPLY or DIVIDE operation?
     A: ______

  #. Q: What about unary operations? How can we set up a number for those?
     A: ______

So, how did you do? I hope you got all the answers right. And I certainly
hope all your answers were the same. Because this is how we manage the
values we want to pass around in the Python VM: they go on the stack!

If we are going to do an add of two numbers, we set it up by putting the
first number on the stack, then putting the second number on the stack, and
then doing a BINARY_ADD, which takes two numbers off the stack, and puts
their sum on the stack.

What we need to do, then, is to trust that all the steps before us have
configured the stack the way it needs to be configured. Thus, if the
add and subtract (and multiply, divide, modulus, ...) operators need a left
operand to be on the stack, we just assume that it's there. (And write lots
of test cases to make *damn sure* that we're right!) Let's give it a try::

    def expr_add():
                    # Assume first addend is already on stack.
        match('+')
        expr_atom() # Read second addend, put on stack.
        emit('BINARY_ADD')

And that's it! As long as we write all the other code correctly, to leave
their results on the stack, we can assume that the incoming parameter is on
the stack, and then add the numbers we need to add, and leave our own
results on the stack.

Let's catch up on our test cases, and then go a little bit farther. Add test
cases for all four basic operations, plus some test cases for operator
precedence. (Feel free to copy them from the tests we wrote in chapter 2!)
Here are mine::

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

The only tricky part is the opcode for division. Remember that I want all
our expressions to use integer values, so we need to use the FLOOR instead
of the TRUE division instruction.

The code itself should be a snap, now. The precedence implementation is the
same - add and subtract call mulop, multiply and divide call atom. If you
have trouble, refer back to chapter 2.

Once you have that working, let's add support for parentheses and multiple
operators (if you didn't add them before). Again, we can take the test cases
from chapter 2. Pay careful attention to the opcodes in
`test_multiple_binops`, below. You have to understand how the additive and
multiplicative precedence levels are working together to predict how the
opcodes will be generated.  Remember that mulop is basically "greedy," while
addop is basically "lazy." ::

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

Another Bug is Found
~~~~~~~~~~~~~~~~~~~~

I made my `expr_atom` function recurse by calling `expression`. (As opposed
to calling `expr_addop`.) I discovered a leeeetle bug: the `expression`
function automatically appends a 'RETURN_VALUE' opcode when it finishes.
Oops! That will have to be moved to `compile`, instead. With that change,
everything worked.

Unary Precedence
~~~~~~~~~~~~~~~~

I promised in chapter 2 that I would re-visit the issue of unary operator
precedence. Before we start working on adding unary operators to our code,
let's do that.

Most programming languages, inspired by the C/Algol family tree, accept
unary operators at pretty much any location. You can negate any single term
just by putting a '-' in front of it.

But there are a lot of mathematicians who feel that this is pointless. If
you need to subtract a number, just subtract it! Don't bother with adding
the negative. They feel that "a - b" is easier to read, and more sensible,
than "a + -b".

In this case, why not move the unary from the highest precedence to the
lowest. Instead of allowing a negative sign in front of every term, why not
allow one negative sign, right at the front of an expression, one time.
Everything else can be handled by changing add to subtract, or subtract to
add, or by wrapping parens around a sub-expression.

My own, personal, bias is to make my expression parser act like C. But if
you're more mathematically inclined, maybe you want to speed things up by
eliminating all the unary minuses except one.

At any rate, I'm going to follow the same path we followed back in chapter
2, and support unary operators just below `expr_atom` in the precedence
hierarchy::

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

    def expr_unary_plus():
        expr_atom()

    def expr_unary_minus():
        expr_atom()
        emit('UNARY_NEGATIVE')

The test cases are simple::

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


Variables
---------

Functions
---------

Assignments
-----------

Multi-Character Tokens
----------------------

White Space
-----------

