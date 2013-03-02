# vim: set noet sts=4 sw=4 ts=4 tw=76:
BUILDDIR = _build
BUILD_HTML = $(BUILDDIR)/html

all: html

clean:
	rm -fr "$(BUILDDIR)"

html:
	mkdir -p "$(BUILD_HTML)"
	find . -iname '*.md'	\
	| while read infile ;	\
	do						\
		pandoc -o "$(BUILD_HTML)/$${infile/.md/.html}" "$$infile"; \
	done

