# config
EXPERIMENT_SUITE_NAMES = \
	concats-balanced \
	concats-extracts-small \
	concats-small \
	different-prefix

# paper config
PAPER          = paper.pdf
INCLUDES_DIR   = includes
PAPER_SECTIONS = $(shell find $(INCLUDES_DIR) -name "*.tex")

# solver config
Z3STR3_REV   = master
Z3STR3_BUILD = trace

CVC4_REV   = latest
CVC4_BUILD = trace

Z3STR3_NAME = z3str3-$(Z3STR3_REV)-$(Z3STR3_BUILD)
CVC4_NAME   = cvc4-$(CVC4_REV)-$(CVC4_BUILD)

Z3STR3 = ~/bin/$(Z3STR3_NAME)
CVC4   = ~/bin/$(CVC4_NAME)

CVC4_CMD   = $(CVC4) --strings-exp --lang smt2.5 -m
Z3STR3_CMD = $(Z3STR3) smt.string_solver=z3str3

ifneq ("","$(wildcard $(CVC4))")
CVC4_TAGS       = $(shell $(CVC4) --show-trace-tags | tr " " "\n" | grep strings)
CVC4_TRACE_ARGS = $(addprefix --trace=,$(CVC4_TAGS))
endif

# directories
DATA_DIR          = data
TRACES_DIR        = $(DATA_DIR)/traces
PROBLEM_DIR       = $(DATA_DIR)/problems
GRAPHS_DIR        = $(DATA_DIR)/graphs
TRACE_PROBLEM_DIR = $(PROBLEM_DIR)/trace

# outputs
TRACE_PROBLEMS    = $(shell find $(TRACE_PROBLEM_DIR) -name "*.*")
EXPERIMENT_SUITES = $(addprefix $(PROBLEM_DIR)/,$(EXPERIMENT_SUITE_NAMES))

GRAPHS = $(addprefix $(GRAPHS_DIR)/,$(addsuffix .png,$(notdir $(EXPERIMENT_SUITE_NAMES))))

Z3STR3_TRACES = $(addprefix $(TRACES_DIR)/$(Z3STR3_NAME)-,$(addsuffix .trace, $(notdir $(TRACE_PROBLEMS))))
CVC4_TRACES   = $(addprefix $(TRACES_DIR)/$(CVC4_NAME)-,$(addsuffix .trace, $(notdir $(TRACE_PROBLEMS))))

# targets
paper: $(PAPER)

watch:
	while true; do make | grep -v "Nothing to be done"; sleep 0.5; done

check: $(CVC4) $(Z3STR3)
	$(CVC4) --version
	$(Z3STR3) --version

traces: $(Z3STR3_TRACES) $(CVC4_TRACES)

graphs: $(GRAPHS)

problems: $(EXPERIMENT_SUITES)

re-gather:
	$(RM) -r $(PROBLEM_DIR)
	$(RM) -r $(GRAPHS_DIR)
	git checkout $(TRACE_PROBLEM_DIR)
	$(MAKE) problems graphs

# real targets
$(TRACES_DIR) $(GRAPHS_DIR) $(PROBLEM_DIR):
	mkdir -p $@

$(Z3STR3):
	cd ../../ && $(RM) -r installed/solvers/z3str3
	cd ../../ && $(MAKE) install_z3str3 Z3STR3_REV=$(Z3STR3_REV) Z3STR3_BUILD=$(Z3STR3_BUILD)

$(CVC4):
	cd ../../ && $(RM) -r installed/solvers/cvc4
	cd ../../ && $(MAKE) install_cvc4 CVC4_REV=$(CVC4_REV) CVC4_BUILD=$(CVC4_BUILD)

# patterns
$(GRAPHS_DIR)/%.png: | $(GRAPHS_DIR)
	cd ../../ && $(MAKE) graphs GRAPHS_ARGS=--no-title \
		WHAT=$* \
		CVC4_REV=$(CVC4_REV) CVC4_BUILD=release \
		Z3STR3_REV=$(Z3STR3_REV) Z3STR3_BUILD=release
	cp ../../experiment/graphs/cactus/$*-cactus.png $@

$(PROBLEM_DIR)/%: | $(PROBLEM_DIR)
	cp -r ../../website/problems/$* $(PROBLEM_DIR)

$(TRACES_DIR)/$(CVC4_NAME)-%.trace: $(TRACE_PROBLEM_DIR)/% $(CVC4)
	-$(CVC4_CMD) $(CVC4_TRACE_ARGS) < $< 2> $@ > $@

$(TRACES_DIR)/$(Z3STR3_NAME)-%.trace: $(TRACE_PROBLEM_DIR)/% $(Z3STR3)
	-$(Z3STR3_CMD) -tr:str $< 2> $@ > $@
	cat .z3-trace >> $@
	rm .z3-trace

# NOTE:
#      not using $(GRAPHS) here because those are real targets, and
#      I don't want this target to generate graphs; I only want it to depend
#      on graphs that are already in the directory (if any)
%.pdf: %.tex $(PAPER_SECTIONS) %.bib $(wildcard $(GRAPHS_DIR)/*)
	latexmk -pdf -bibtex $<

# maintenance targets
clean:
	latexmk -C
	$(RM) *.fdb_latexmk *.fls *.run.xml *.bbl *.lol
