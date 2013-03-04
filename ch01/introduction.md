---
layout: chapter
title: Introduction
---
Introduction
============

I am not an academic. I'm not trying to get a Ph.D. I'm not worried about
tenure, or publishing. So I don't have much of an interest in the "Theory of
Computation." I have this in common with Jack Crenshaw: I would much rather
write some code that works, than spend page after page playing games with
sets and theorems and such.

Like Jack, I have a great deal of respect for the accomplishments of the
academics that have established the basis for what we are doing here.  But
as with the guys that maintain the public sewer system, I prefer to
appreciate their work from afar.

So I'm not going to go into detail about a bunch of theory stuff. That
doesn't mean I won't use it. And it doesn't mean I won't refer you to
it. I just means that I've already said more than I really want to about
it. So I'll stop.

The Development Environment
---------------------------

Instead, let's talk about what we are going to need to get moving on
this project. The first thing is a software development environment. If
you're on a Mac, or a Linux box, then you're almost there. If you're on
a Windows box, you have a little more work cut out for you. I'd
recommend you do the following:

- Get a a recent version of Python 3. I'm using 3.3 on a Mac. Once
  you have that running, make sure you can use pip. Get the nose
  testing package.
- Get a good Python program editor. I'm using vim inside iTerm on my
  Mac. PC users might want to try notepad++.
- Get a copy of git, a distributed version control tool. It will let
  you download all the source code.

The Project Layout
------------------

If you have a copy of the source repository, you can see that I have a
separate subdirectory for each chapter. Each chapter is a separate
'project' that doesn't depend on any of the earlier chapters. And so,
each project has its own suite of tests. For this chapter, the directory
structure looks like:

    lbac-python/
        :   -   ch01/
            :   -   tests/
                :   *.py
            -   cradle.py ...

Each chapter will have a tests/ subdirectory. And each chapter will have
its own copy of `cradle.py` -- a file we're going to write in this
chapter, that contains a bunch of common, low-level routines.

The Cradle
----------

We're going to be writing a bunch of common functions, and counting on
them later. So now is the time to make sure they work perfectly. Let's
take a look at what is needed, and how our "cradle" will work.

> -   *Error Reporting*
>     :   -   abort(msg) reports an error and ends the program by
>             causing a SystemExit exception to be raised (calling
>             'exit').
>
>         -   error(msg) reports an error.
>
>         -   expected(what) aborts with a message explaining that a
>             particular input was expected.
>
> -   *Input*
>     :   -   Peek, a global, holds the next character that will be
>             returned by the input system.
>
>         -   get\_char() will read in another character from the input
>             stream. It returns the previous value of Peek. When the
>             input stream is exhausted, returns None.
>
>         -   get\_number() returns a number.
>
>         -   get\_word() returns a word - either a variable name or a
>             language keyword.
>
>         -   match(ch) requires that the next character match its
>             argument. It advances the input by calling get\_char(),
>             and returns the result.
>
> -   *Output*
>     :   -   emit(text) writes out some text.
>
>         -   emitln(text) writes out a line of text plus a newline.
>
>         -   init() performs initialization of the cradle.
>
>         -   main() calls init then calls compile.
>
It may surprise you that the cradle is a collection of functions - there
are no objects, no classes, no complex data types. This is for
simplicity more than anything else- we're at chapter 1 here, we don't
need anything fancy. One thing that hasn't changed in 25 years is the
KISS principle: Keep it simple stupid. Of course, now we wrap that up in
'Agile,' and say YAGNI: You Ain't Gonna Need It. Very few programs need
two parsers, or two parallel input streams, or two parallel outputs.
Certainly, we don't.

Next, there is a global variable in there. What's up with that? Well, I
could wrap all the accesses to it in a function... but why? We all know
what happens when I access that variable. Pretend it's a property, if it
makes you feel better.

Finally, where's the code? The included cradle.py only contains a
definition for main! Well, there's all those test cases in
ch01/tests/\*.py. You'd best get started...

Also, remember that the cradle is just that- a cradle. It's where things
get started, not where they finish. I've put my versions of the
functions in ch01.py. I'll copy that to be the cradle for chapter 2.
There's nothing too complex in the cradle, though, so I'd strongly
suggest that you try coding it yourself. If nothing else, it will help
to keep me honest by forcing me to work through the interface I've
defined.

Either way, fire up your development environment and run some code. Make
sure that some version of the cradle actually works, and then get ready
for the next chapter. It'll be about expression parsing. Because the
beginning is always about expression parsing.
<!---
vim: set et fileencoding=utf8 sts=4 sw=4 ts=4 tw=76:
-->
