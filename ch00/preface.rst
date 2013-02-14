.. vim: set tw=76

Preface: 25 years later
=======================

I don't know exactly when he started composing the series, but between July of
1988 and May of 1995 Jack Crenshaw published a series of articles titled
:title:`Let's Build a Compiler!`

That series remains perhaps the best available reference for codes interested
in the process of developing a :term:`*Language Processor*` such as a
syntax hilighter, SLOC counter, static analyzer, interpreter or compiler.

Because of the enduring quality of the series, and because I find myself (25
years later) sharing a lot of interests in common with the Jack Crenshaw of
1988, I have decided to write my own compiler. And document the process. To
make things a little easier on everyone involved, I won't use Borland Turbo
Pascal. Instead, I have decided to use Python 3.

Scope
-----

I'm ambitious, but not insane. I want to explore writing a compiler, not
exhaustively cover every possible aspect of the process. What's more, I
have no desire whatsoever to present any math. This is my writing about
coding, not about mathing. Hell! That's not even a word.

The idea will be to develop a compiler, plus some supporting tools, that
does what you expect a compiler to do: accept source code of some kind
as input, and emit some kind of compiled code as output.

Unfortunately, at the time of this writing, Python 3 has not been
universally adopted by the Python community. So many of the helper
modules that might be available in 2.x aren't available to me. So there
may be more 'supporting tools' written than you are comfortable with.

Structure
---------

From a very general perspective, a *Language Processor* does two things:
first it reads in one or more files in a language and builds up some
kind of understanding of the code; and second it uses the understanding
built up in the first part to perform whatever tasks are requested of
it. 

Consider a syntax highlighter: a highlighter doesn't really
need to know about the language, except to identify the boundaries beween
words. Once it knows that a string of characters is an identifier- and
not, say, a key word like 'if' or 'while'- the 'understanding' part is pretty
much done. "Color this one blue!"

My objective, as stated above, is to build a 'real compiler'. Not a
syntax highlighter, but a program that will take source code in, and
write some kind of executable out. I'm willing to settle for
*translating* the code to a much lower level (writing out assembly files
instead of compiled objects) but that's about it. 

The structure, then, will be "the full monty". If you've dabbled with
compilers before, you'll recognize the stages: lexer, parser, tree,
optimizer, code generator. I want to touch on all of those in this
series.

Just like in the Jack Crenshaw's original series, I expect we'll have to
take things apart and put them back together a few times. I don't expect
to start writing code and just emit all the parts in working order.
There is going to be some give and take - in fact, a lot of it.
Hopefully it will help increase my (and your) understanding, and not
just piss you off.

Approach
~~~~~~~~

In all of my reading, I haven't found much test-driven work around
compilation. That surprises me, since compilers are complicated systems,
and since it can be really hard to guess where a failure is coming from.
So there will be tests, and many of them will be written in advance. I
expect more of them will be written afterwards - I'll want to set
regression barriers, too.
