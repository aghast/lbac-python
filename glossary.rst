.. vim: set noet sts=4 sw=4 ts=4 tw=75:

.. glossary::

Glossary
========

Language Processor
	Any one of several classes of utility program that parses an input
	document, written in a *language* that is *recognized* by the program,
	then acts upon the input in some manner.

	At a low level, reading a configuration file that has a prescribed
	format can be considered processing the configuration file language.
	But in general configuration files are processed based on their
	format-- that is, the shape of the contents. Whereas language
	processing depends more on the contents of the input than the shape.

	Programming language compilers and interpreters are certainly language
	processors. But in many cases, documentation utilities that rely on a
	particular commenting convention are also language processors, in they
	they have to understand the source code in order to associate
	particular documentation elements with the corresponding symbol names
	in the code. Likewise, some syntax highlighter modules work by parsing
	the input programming language. Those are definitely language
	processors.

