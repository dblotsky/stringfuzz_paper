PAPER = paper.pdf
INCLUDES_DIR = includes
SECTIONS = $(shell find $(INCLUDES_DIR) -name "*.tex")

Z3STR3_REV=master
Z3STR3_BUILD=trace

CVC4_REV=latest
CVC4_BUILD=trace

Z3STR3_NAME=z3str3-$(Z3STR3_REV)-$(Z3STR3_BUILD)
CVC4_NAME=cvc4-$(CVC4_REV)-$(CVC4_BUILD)

Z3STR3=~/bin/$(Z3STR3_NAME)
CVC4=~/bin/$(CVC4_NAME)

TIMEOUT=300

DATA_DIR=data
TRACES_DIR=$(DATA_DIR)/traces
REAL_PROBLEM_DIR=$(DATA_DIR)/problems/release
TRACE_PROBLEM_DIR=$(DATA_DIR)/problems/trace
RESULTS_DIR=$(DATA_DIR)/results

CVC4_CMD=$(CVC4) --strings-exp --lang smt2.5 -m
Z3STR3_CMD=$(Z3STR3) smt.string_solver=z3str3

REAL_PROBLEMS=$(shell find $(REAL_PROBLEM_DIR) -name "*.*")
TRACE_PROBLEMS=$(shell find $(TRACE_PROBLEM_DIR) -name "*.*")

Z3STR3_TRACES=$(addprefix $(TRACES_DIR)/$(Z3STR3_NAME)-,$(addsuffix .trace, $(notdir $(TRACE_PROBLEMS))))
CVC4_TRACES=$(addprefix $(TRACES_DIR)/$(CVC4_NAME)-,$(addsuffix .trace, $(notdir $(TRACE_PROBLEMS))))

ifneq ("","$(wildcard $(CVC4))")
CVC4_TAGS=$(shell $(CVC4) --show-trace-tags | tr " " "\n" | grep strings)
CVC4_TRACE_ARGS=$(addprefix --trace=,$(CVC4_TAGS))
endif

# targets
paper: $(PAPER)

watch:
	while true; do make | grep -v "Nothing to be done"; sleep 0.5; done

check: $(CVC4) $(Z3STR3)
	$(CVC4) --version
	$(Z3STR3) --version

# gather-real:
	# ../../bin/timesolver.py $(CVC4_NAME) "$(CVC4_CMD) < " --verbose --timeout $(TIMEOUT) --format csv --problem-list $< > $(RESULTS_DIR)/cvc4.csv
	# ../../bin/timesolver.py $(Z3STR3_NAME) "$(Z3STR3_CMD) " --verbose --timeout $(TIMEOUT) --format csv --problem-list $< > $(RESULTS_DIR)/z3str3.csv

$(TRACES_DIR)/$(CVC4_NAME)-%.trace: $(TRACE_PROBLEM_DIR)/% $(CVC4)
	-$(CVC4_CMD) $(CVC4_TRACE_ARGS) < $< > $@

$(TRACES_DIR)/$(Z3STR3_NAME)-%.trace: $(TRACE_PROBLEM_DIR)/% $(Z3STR3)
	-$(Z3STR3_CMD) -tr:str $< > $@
	cat .z3-trace >> $@
	rm .z3-trace

gather: $(Z3STR3_TRACES)
gather: $(CVC4_TRACES)

# real targets
$(RESULTS_DIR) $(TRACES_DIR):
	mkdir -p $@

$(Z3STR3):
	cd ../../ && $(RM) -r installed/solvers/z3str3
	cd ../../ && $(MAKE) install_z3str3 Z3STR3_REV=$(Z3STR3_REV) Z3STR3_BUILD=$(Z3STR3_BUILD)

$(CVC4):
	cd ../../ && $(RM) -r installed/solvers/cvc4
	cd ../../ && $(MAKE) install_cvc4 CVC4_REV=$(CVC4_REV) CVC4_BUILD=$(CVC4_BUILD)

%.pdf: %.tex $(SECTIONS) %.bib
	latexmk -pdf -bibtex $<

clean:
	latexmk -C
	$(RM) *.fdb_latexmk *.fls *.run.xml *.bbl *.lol
