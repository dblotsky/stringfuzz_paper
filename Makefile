PAPER = paper.pdf
INCLUDES_DIR = includes
SECTIONS = $(shell find $(INCLUDES_DIR) -name "*.tex")

paper: $(PAPER)

# real targets
%.pdf: %.tex $(SECTIONS) %.bib
	latexmk -pdf -bibtex $<

clean:
	latexmk -C
	$(RM) *.fdb_latexmk *.fls *.run.xml *.bbl *.lol
