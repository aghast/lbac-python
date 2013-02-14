.. vim: set tw=76

Introduction
============

I am not an academic. I'm not trying to get a Ph.D. I'm not worried about
tenure, or publishing. So I don't have much of an interest in the "Theory of
Computation." This is another thing that I have in common with Jack
Crenshaw: I would much rather write some code that works, than spend page
after page playing games with sets and theorems and such.

Like Jack, I have a great deal of respect for the accomplishments of the
academics that have established the basis for what we are doing here. But
much like the guys that maintain the public sewer system, I would rather
appreciate their excellent work from afar than join them.

So I'm not going to go into detail about a bunch of theory stuff. That
doesn't mean I won't use it. And it doesn't mean I won't refer you to it. I
just means that I've already said more than I really want to about it. So
I'll stop.

The Development Environment
---------------------------

Instead, let's talk about what we are going to need to get moving on this
project.  The first thing is a software development environment. If you're
on a Mac, or a Linux box, then you're almost there. If you're on a Windows
box, you have a little more work cut out for you.  I'd recomment you do the
following:

   * Get a a recent version of Python 3. I'm using 3.3 on a Mac. Once you
     have that running, make sure you can use pip. Get the nose testing
     package.
   * Get a good Python program editor. I'm using vim inside iTerm on my Mac.
     PC users might want to try notepad++.
   * Get a copy of git, a distributed version control tool. It will let you
     download all the source code.

With all that in hand, let's move on to writing some code.

The Project Layout
------------------

If you have a copy of the source repository, you can see that I have a
separate subdirectory for each chapter. Each chapter is a separate 'project'
that doesn't depend on any of the earlier chapters. And so, each project has
its own suite of tests. For this chapter, the directory structure looks
like:

   path/to/root/
       + ch01/
           + tests/
              =*.py=
           + cradle.py
             ...

Each chapter will have a tests/ subdirectory. And each chapter will have its
own copy of =cradle.py= -- a file we're going to write in this chapter, that
contains a bunch of common, low-level routines.

The Cradle
----------

We're going to be writing a bunch of common functions, and counting on them
later. So now is the time to make sure they work perfectly. Let's take a
look at what is needed, and how our "cradle" will work.

  * `abort(msg)` reports an error and ends the program by causing a
    SystemExit exception to be raised (calling 'exit').

  * `error(msg)` reports an error.

  * `expected(what)` aborts with a message explaining that a
    particular input was expected.

  * `Peek`, a global,  holds the next character that will be returned by
    the input system.

  * `get_char()` will read in another character from the input
    stream. It returns the previous value of Peek. When the input stream is
    exhausted, returns None.

  * `get_number()` returns a number.

  * `get_word()` returns a word - either a variable name or a
    language keyword.

  * `match(ch)` requires that the next character match its argument.
    It advances the input by calling get_char(), and returns the result.

  * `emit(text)` writes out some text.

  * `emitln(text)` writes out a line of text plus a newline.

  * `init()` performs initialization of the cradle.

  * `main()` calls `init` then calls `compile`.

First, the cradle is a collection of functions - there are no objects, no
classes, no complex data types. This is for simplicity more than anything
else. Very few programs need two parsers, or two parallel input streams, or
two parallel outputs. Certainly we don't need to be dealing with extra
complexity when we're just getting started.

Second, there is a global variable in there. What's up with that?
Well, I could wrap all the accesses to it in a function. But why? We all
know what happens when I access that variable. Pretend it's a property, if
it makes you feel better.

Finally, where's the code? The included cradle.py only contains a definition
for `main`! 

Well, there's all those test cases in `ch01/tests/*.py`. You'd best get
started...
