.. vim: set fileencoding=utf8 tw=76
.. Let's Build a Compiler (in Python)! chapter 2 text file.
   Created Thu Feb 14 09:59:43 EST 2013, by austin.

Expression Parsing
=================

The first part of parsing is always expression parsing. Why is that?
Well, probably because it's a simple, straightforward task with a little
bit of complexity but not too much, and because everybody already knows
the rules. We could make the first chapter about scanning sentences in
Thai, where they don't actually use spaces to separate the words. But,
statistically, not to many of my readers are going to be familiar with
Thai. And we would be jumping in at the very, very deep end, instead of
getting our feet wet in the shallows. So we won't do that.  We'll do
expressions instead. (Sorry, Thai readers!)

You should have a Python 3 development environment up and running. And
you should already have run the test cases from chapter 1. I have copied
my version of the cradle code from chapter 1 to ch02/cradle.py. If you
wrote your own versions, I encourage you to copy them over mine. Make a
copy of the cradle in the ch02 directory, and let's get started!

When we talk about expressions, we mean mathematical expressions. The
right-hand side of equations like the one below.

    y = mx + b

Except that computer languages usually require an operator to indicate
multiplication, since they allow variable names of more than one letter.

The Simplest Expression
-----------------------

The simplest expression is a single number. Let's see if we can
recognize that. In your copy of the chapter 2 cradle, add a new definition
for the `compile` function:

    def compile():
        expression()

We'll keep that throughout this chapter, since we're all about parsing
expressions right now.

Now let's parse our simple expression:

    def expression():
        """Parse a very simple expression."""
        emitln("Result: " + get_number())

Run that. You should get an output something like this::

    Enter your code on a single line. Enter '.' by itself to quit.
    1
    Result: 1
    2
    Result: 2
    3
    Result: 3
    .

At this point, you have a working expression parser. It's not a compiler.
It's not a four-function calculator. But it does parse a well-defined subset
of mathematical expressions correctly.

At this point, we have a choice. We can start working towards parsing more
types of expressions, or we can work more towards compiling the code we have
into some kind of runnable format. Because we're just getting started, and
because of the first rule, [1]_ I'm going to carry on with the expression
parsing part, and leave the code generation for later.

Binary Expressions
------------------

Everyone understands four-function calculators. A few numbers, a couple of
operator symbols. Maybe there's a memory function, that nobody really uses.
Let's head in that direction with our code. We'll add some operators and see
how that works.

First, let's define our operators. We're going to use the standard plus (+),
minus(-), and multiply(*) from most C-like languages. We'll be using the
division(/) operation, too, but we'll do integer division rather than
floating point. (At this point, Python is handling the math for us, so we
could support floating point easily. But when we're compiling to some other
code, I don't want to set expectations too high.)

As everyone knows, a binary expression looks like "1 + 2" or "8 / 4". Our
`expression` code can handle that. Just remember that `get_number` returns
a string::

    def expression():
        num1 = int(get_number())
        operator = get_char()
        num2 = get_number()
        fn = {
            '+': lambda x,y: x+y,
            '-': lambda x,y: x-y,
            '*': lambda x,y: x*y,
            '/': lambda x,y: x/y,
        }[operator]
        emitln("Result: %d" % fn(num1, num2))

The output looks good::

    Enter your code on a single line. Enter '.' by itself to quit.
    1+7
    Result: 8
    9-3
    Result: 6
    2*5
    Result: 10
    9/2
    Result: 4
    .

If you have never encountered, or never used, Python's `lambda` before, it's
one of those things that might seem complex and terrifying because of all
the functional mumbo-jumbo surrounding it. But basically it just defines a
quick function. Saying `lambda args: expression-with-args` is just a fast
way of saying::

    def anonymous_fn_name(args):
        return expression-with-args

Lambdas are only allowed to contain a single expression - the things we are
now learning how to parse. Like a lot of other things, keep it simple and
you'll keep it easy.

Now, try parsing one of the single-digit expressions from our earlier
version. It seems like our binary-expression parser is a little too
demanding. What exactly happened, there? ::

    3

    'Number' expected.

Looking at the code for `expression` we can see that the first call to
`get_number` would return the '3' that was input. The next call, to
`get_char` is going to get whatever is returned next - including the None
that is returned at end of input. We don't do any kind of checking on that
input, and that's a problem by itself. Next, though, we get another call to
`get_number` that *does* validate its input. And that is where the error
is coming from.

There are a couple of problems, so let's try to solve them all together.
First, our code no longer allows simple expressions. So it's time to put in
a test suite, with some regression tests to make sure we don't "lose" any
more behavior. And then we'll have to allow for the possibility of either
simple single-digit expressions or more complex binary expressions. And
finally, we'll want to test for legal operators in a more active fashion.

Testing Framework
~~~~~~~~~~~~~~~~~

We're going to be doing a lot of the same kind of test: call our code with a
particular input string, and assert that the output matches a given string.
Before we do anything else, let's add a helper for that to the
cradle_tests.py file in the tests directory. Here's my stab at it::

    class TestCradle(unittest.TestCase):

        def assertExpr(inp, result):
            want = "Result: %d" % int(result)
            compiler.init(StringIO(inp))
            compiler.compile()
            output = self.stdout.getvalue().split("\n")[-2]
            self.assertEqual(output, want)

Make a copy of the ch02/tests/cradle_tests.py module to another name in the
tests directory. I called my first parser expr1.py, so I'll use
expr1_tests.py. Then let's write some tests::

    def test_add(self):
        self.assertExpr('1+8', 9)
        self.assertExpr('7"4', 11)

    def test_subtract(self):
        self.assertExpr("8-3", 5)
        self.assertExpr("4-4", 0)

    def test_multiply(self):
        self.assertExpr("3*2", 6)
        self.assertExpr("1*8", 8)

    def test_divide(self):
        self.assertExpr("2/2", 1)
        self.assertExpr("3/2", 1)
        self.assertExpr("6/2", 3)

Run nosetests and make sure everything is working as expected. Note that in
Python 3 the default division behavior has changed - integers return
floating point results unless the 'floor division' operator (//) is used.
Testing for this is important.

Once you have a working set of binary expression test cases, let's go back
and add some regression tests to handle the "simple expression" case you
handled before::

    def test_simple(self):
        self.assertExpr("1", 1)
        self.assertExpr("9", 9)

Whoops! That test doesn't pass, does it? And it still doesn't produce a very
good message describing the problem. Let's add a test case, and some more
code::

    def test_bogus_operator(self):
        with self.assertRaises(SystemExit):
            self.assertExpr("1^1", 1)
        self.assertEqual(self.stderr.getvalue(), "\n'BinOp' expected.\n")

Checking Every Input
~~~~~~~~~~~~~~~~~~~~

Now we can check for a valid operator before we do anything with it::

    _binop_sw = {
        '+': lambda x,y: x+y,
        '-': lambda x,y: x-y,
        '*': lambda x,y: x*y,
        '/': lambda x,y: x//y,
    }

    def expression():
        result = int(get_number())
        if Peek is None:
            return

        if Peek in _binop_sw:
            op = get_char()
            num2 = int(get_number())
            result = _binop_sw[op](result, num2)
        else:
            expected('BinOp')

In this version of `expression(),` the table of lambdas has been moved out
to be a global, mainly for readability. The code now checks before calling
`get_char` to see if there is an operator character, and if so it confirms
that the operator is a BinOp before trying to do anything with it.

A Bug is Found
~~~~~~~~~~~~~~

Adding this change reduces our test failures to one. We are handling the
simple expression case, and it looks like this code should work, but it
turns out there is a bug in the `get_char` code - the :py:meth:`File.read`
method is defined as being able to return an empty string in cases when no
bytes are available for reading. This is intended for asynchronous devices -
like a keyboard - where it makes sense to check for some input now, and
check again later in case the user types something. But for our
:py:class:`StringIO` objects, returning an empty string means that the
object has reached its end, and so we should consider that to mean EOF for
this program.

Let's fix `get_char` now, test case and all. First, the test case::

    def test_read_at_eof(self):
        compiler.init(StringIO('ab'))
        self.assertEqual(compiler.get_char(), 'a')
        self.assertEqual(compiler.get_char(), 'b')
        self.assertIsNone(compiler.get_char())

Next, run the tests, which shows us this error::

    ======================================================================
    FAIL: test_read_at_eof (expr1_tests.TestCradle)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/Users/austin/git/lbac/ch02/tests/expr1_tests.py", line 61, in
      test_read_at_eof
          self.assertIsNone(compiler.get_char())
          AssertionError: '' is not None

Finally, let's fix this problem::

    def get_char():
        """
        Advance the input to the next character. Return the character consumed,
        or None. Note that this function changes `Peek`, and returns the *old*
        value of `Peek`.
        """
        global Peek
        result = Peek
        Peek = _Input.read(1) if _Input.readable() else None
    >    if Peek == '':
    >        # StringIO and tty objects can be 'readable but empty now'.
    >        Peek = None
        return result

With those changes installed, the code works as expected. The `get_char`
function now returns None when it reaches the end of the string buffer, and
the expression-parsing code now handles both the *simple* and *binary*
expression types, as needed.

Really Long Expressions
~~~~~~~~~~~~~~~~~~~~~~~

Sadly, however, the code only handles a single binary operator. We can't
input a string of operations, like 1+2*4/3, and get an answer. Let's add
a test case for multiple binary operatos::

    def test_multiple_binops(self):
        self.assertExpr("1+2*4/3", 4)
        self.assertExpr("8-5+3/6*9", 9)

This doesn't pass, because our expression parser only expects a single
operator. We'll have to make some changes to the expression parser- adding a
loop, in particular- to get this to work. Go ahead and put a loop in the
expression code, to handle multiple operators::

    def expression():
        result = int(get_number())
    >   while Peek is not None:
            if Peek in _binop_sw:
                op = get_char()
                num2 = int(get_number())
                result = _binop_sw[op](result, num2)
            else:
                expected('BinOp')
        emitln("Result: %d" % result)

Finally, with the while loop added to the mix, we have an expression parser
that will accept an arbitrarily long string of binary operations, maintain a
running result, and print the result at the end of the expression.

But in compiler terms, it's a little too much like a desk calculator, and
not enough like a programming language. The problem now is a lack of support
for "operator precedence."

Operator Precedence
-------------------

Precedence and associativity are the properties of an operator that
determine the specific order in which an expression containing that operator
is evaluated. For example, which of the following is correct? ::

    1 + 3 * 5 = 20

    1 + 3 * 5 = 16

In fact, both of them are. You just have to perform the operations in a
different order. If you use a 4-function calculator to do this, you find
that it greedily evaluates each operation as soon as possible. The result is
that the expression is evaluated as (1+3)=4, and then (4*5)=20.

On the other hand, if you follow the generally-accepted 'rules of algebra,'
you evaluate the sub-expression involving multiplication first, and then do
the addition. This resolves as (3*5)=15, and then (1+15)=16.

I don't know about you, but I am very, very accustomed to counting on
operator precedence. I think we need to have it for any serious expression
evaluator. So let's add a test case::

    def test_mul_add_precedence(self):
        self.assertExpr("1+3*5", 16)
        self.assertExpr("9-6/2", 6)

Surprise! It doesn't pass::

    AssertionError: 'Result: 20' != 'Result: 16'
    - Result: 20
    ?         ^^
    + Result: 16
    ?         ^^

In our simple algebraic expressions, we need to differentiate between
addition and subtraction, with lower precedence, and multiplication and
division, with higher precedence. Our problems spring from binary operators,
so we don't have to worry about the numbers. What we have to worry about are
four different scenarios, determined by the operators:

#. term + term + term
#. term + factor x factor
#. factor x factor + term
#. factor x factor x factor

And in fact, two of those we don't have to worry about at all- when the
operators all have the same precedence, there should be no problem. So let's
look at the cases where the precedences are different. In case #2, we know
that the later subexpression should be resolved before we proceed. In case
#3, we know that the earlier subexpression should be resolved before the
later one.

So here's some pseudo-code, for use with additive operations::

    def additive:
        get a number
        if no operator, return the number
        read the operator
        get a number
        look for another operator
        if no other operator,
            return the result of the operator on the two numbers.
        if the operator is multiplicative, go resolve that first
        else go ahead and evaluate the current operator
        proceed with the next operator

That's...awkward, at first. But let's look at multiplicative operators.
Here's a similar set of pseudo-code::

    def multiplicative:
        get a number
        if no operator, return the number
        read the operator
        if the operator is not multiplicative, stop and return the number.
        get a number
        perform the operation
        if no operator, return the result
        read the opeator
        if the operator is not multiplicative, stop and return the result
        get a number
        perform the operation
        ...

That code actually looks pretty clean. I can see evidence of a loop in
there. Let's try some Python. I'll use the switching-dict idea, with the
lambda functions, that I used before. ::

    def expr_mul():
        result = int(get_number())
        if not Peek in _mulops_sw:
            return result
        op = get_char()
        num2 = int(get_number())
        result = _mulops_sw[op](result, num2)
        if not Peek in _mulops_sw:
            return result
        op = get_char()
        num2 = int(get_number())
        ...

And now the loop is very clear. So let's rewrite it again, with the loop::

    def expr_mul():
        """
        Handle multiplicative sub-expressions.
        """
        result = int(get_number())
        while Peek in _mulops_sw:
            op = get_char()
            num2 = int(get_number())
            fn = _mulops_sw[op]
            result = fn(result, num2)
        return result

With the multiplicative case handled, let's go back and re-evaluate the
arithmetic case. There was a lot of checking in that case for multiplicative
operators. But if we have that case reference this case, we won't need to
deal with the multiplicative operators. So the additive case looks like:

    def additive:
        get a number, or a multiplicative sub-expr
        if no operator, return the result.
        read an additive operator.
        get a number, or a multiplicative sub-expr
        evaluate the additive operator
        check for another operator
        ...

From this, it becomes obvious that the additive case looks a lot like the
multiplicative case. Let's go directly to Python::

    def expr_add():
        """
        Handle additive sub-expressions. Call expr_mul() as needed.
        """
        result = expr_mul()
        while Peek in _addops_sw:
            op = get_char()
            num2 = expr_mul()
            fn = _addops_sw[op]
            result = fn(result, num2)
        return result

Boy! Those sure do look similar! And well they should, since they're doing
the same thing. It's just that we're using two different functions, with a
relationship between them, to model the precedence relationship between the
additive and multiplicative operations.

Let's add those two functions to the code, and change the `expression` to
call `expr_add`. I don't know about you, but when I did that I got a bunch
of test failures. I had to go fix up some places where I was testing
multiple operators and I used the flat 4-function calculator precedence
instead of the standard precedence. Also, my test case for detecting bogus
operators has failed, and I don't have a good idea about how to get it back.
I'm going to mark it as `@skip` for now, in case I get smarter later on.
With that change made, I'm back to all tests passing.

Parentheses
~~~~~~~~~~~

Sometimes you need to override operator precedence. When you want an
additive operation to be done before a multiplicative one, the answer is to
use parentheses. Parens, for short, are an "operator" that has an even
higher precedence than multiplication. By definition, a parenthesized
sub-expression has the same precedence as a number. Here is a test case::

    def test_paren_expr(self):
        self.assertExpr("(3)", 3)
        self.assertExpr("(1+7)", 8)
        self.assertExpr("(1+1)*5", 10)


Without looking too far ahead, it's pretty obvious that variables are also
going to be treated just like numbers. So let's go ahead and create a
`expr_atom` function that will handle these cases for us. We'll define it to
take words, numbers, or parenthesized sub-expressions::

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

Add this function to your code, and change the `expr_mul` function to call
`expr_atom` instead of `get_number`. Suddenly, the paren_expr test has a
weird error. What gives? ::

    TypeError: %d format: a number is required, not NoneType

Here's a hint: we weren't calling `expression` recursively before now. Oops!
Once that issue is fixed, the test cases all pass.

Unary Operators
~~~~~~~~~~~~~~~

There's one more thing we haven't dealt with yet in parsing expressions:
what if something comes with a negative (or positive) sign? Let's add a test
case, so we're clear on what I'm talking about::

    def test_unary_sign(self):
        self.assertExpr('-1', -1)
        self.assertExpr('-2*3', -6)
        self.assertExpr('+8-3', 5)

Yikes! Not only did it not work, but I didn't even get a nice looking error
message. This area definitely needs some work done on it!

The error message problem is because we are capturing all the output,
including stderr, in our test framework. That's my own fault, so I'll give
it a pass, for now.

The lack of support for a plus or minus sign is really a much larger problem
that is masked by the familiarity of the plus and minus. In reality, a
leading plus or minus is a completely different thing from a plus or minus
between two numbers. A leading minus is a *unary minus,* which is completely
different from the *binary minus* that appears between two numbers. 

For comparison, consider the '&' operator in C. There are two flavors, a
unary and a binary flavor. The binary flavor represents *bitwise and* and
computes an integer result from integer arguments. The unary flavor
represents *address of* and computes a pointer result from any non-register
lvalue. Thus, 0x01 & 0xFF yields 0x01. But &foo yields a pointer value, the
address of the object referred to as 'foo'. The operators look the same -
the '&' character - but they have nothing to do with one another.

The same is true for unary and binary minus, or plus. We have to keep in
mind that they have a different syntax - unary vs. binary - and have
different meanings. And when we move towards compiling to executable code,
they will be probably be implemented with different opcodes.

With all that said, what are the rules for unary operators? In C, the unary
operators all share a common precedence level, and use order of appearance
to determin order of execution. I'll make the suggestion here that this is
not the only solution. We'll go with the 'C way' for now, but I'll revisit
this issue later, when we look at Boolean expressions.

So, if we are assigning unary operators a very high precedence, the obvious
place to insert them in the chain is right before `expr_atom`. We can create
an `expr_unary` rule, and add it between `expr_mul` and `expr_atom.`

Let's give that a try now::

    def expr_unary():
        """
        Handle unary operators, like +3 or -9.
        """
        if Peek in _unaryops_sw:
            op = get_char()
            fn = _unaryops_sw[op]
            num = expr_unary()
            result = fn(num)
        else:
            result = expr_atom()
        return result

Adding the link from `expr_mul` just means replacing calls to `expr_atom`
with calls to our new function. Go ahead and do that now, and see what the
test suite has to say. Done correctly, this should address the unary
problem. (Filling in the lambdas should be obvious.)



