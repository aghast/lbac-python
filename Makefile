# vim: set noet sts=8 sw=8 ts=8 tw=76
#
#
OUTPUT_DIR   := _site/
MD_FILES     := $(shell find ch* -name '*.md') index.md
HTML_FILES   := $(MD_FILES:%.md=$(OUTPUT_DIR)%.html)

PANDOC        = /usr/local/bin/pandoc
PANFLAGS      = --email-obfuscation=references \
	      --normalize \
	      --smart \
	      --standalone \
	      --variable lang=en \

TOC_TEMPLATE := $(shell mktemp -t lbac)

.PHONY: all
all: pandoc ;

.PHONY : clean
clean:
	@$(RM) $(HTML_FILES) toc.mdi

.PHONY : pandoc
pandoc: $(HTML_FILES) toc

.PHONY : toc
toc: toc.mdi

toc.mdi: Makefile $(MD_FILES) 
	@$(RM) $(TOC_TEMPLATE)
	echo '$$toc$$' > $(TOC_TEMPLATE)
	cat $(TOC_TEMPLATE)
	$(PANDOC) $(PANFLAGS) --toc --to markdown		\
		--template=$(TOC_TEMPLATE)			\
		$(MD_FILES)					\
	| sed -e 's/^\(-   \)\(.*\)/\1[\2](ch00\/ch00.html)/'	\
	    -e 's/^\(  *-   \)\(.*\)/\1[\2](ch00\/ch00.html#\2)/'\
	> $@
	@$(RM) $(TOC_TEMPLATE)

$(OUTPUT_DIR)%.html :: %.md
	$(PANDOC) $(PANFLAGS) --toc -o $@ $<
