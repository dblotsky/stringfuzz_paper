Introduction
============

In the provided virtual machine, you will find the artifacts described in
the StringFuzz paper submitted for review. All of them are located in
the directory /home/cav/artifact.

Instructions
============

The provided machine image, stringfuzz.ova, is a copy of the cav18.ova file
provided on the CAV 2018 Artifact Submission and Evaluation page.

To load the machine image, open it with VirtualBox, and then start the created
VM (it should be called "cav18").

We created this image and ran the experiments in it (but not the paper)
on an Apple MacBook Pro with a 2.3 GHz Intel Core i7 CPU and 16GB of RAM. In
contrast, we ran the experiments in the paper on real hardware running
Ubuntu Linux 16.04, with a 3.40GHz Intel Core i7-6700 CPU and 32GB of RAM.

Layout
======

In the virtual machine, in directory /home/cav/artifact, you will find the
following directories and files:

    bin/                # scripts used to run experiments and generate instances
    checksum.sha1       # the checksum for this machine image
    instances/          # the instance repository we generated with StringFuzz
    packages/           # zipped source for some of the solvers we tested
    README.tx           # this file
    sample-experiments/ # a sample of experimental data for you to reproduce
    solvers/            # the compiled solvers for use in the experiments
    stringfuzz/         # the source code for the StringFuzz fuzzer

Artifact: Instances
===================

To generate the suite of instances, run the command:

    python3 bin/make_instances.py ./instances

This command invokes the generators directly from Python to avoid shell
overhead, but all of its commands can also be carried out 1-by-1 in a shell
script.

Artifact: Stringfuzz
====================

The StringFuzz tool is already installed on the computer, and its executables
can be run as follows:

    stringfuzzg -h # the instance generator
    stringfuzzx -h # the instance transformer
    stringstats -h # the instance analyser

The source code for the tool resides in stringfuzz/. The source tree looks
like this:

    stringfuzz/
        bin/
            stringfuzzg   # the generator executable
            stringfuzzx   # the transformer executable
            stringstats   # the analyser executable
        stringfuzz/
            generators/   # contains generator modules
            transformers/ # contains transformer modules
            analyser.py   # used by stringstats to analyse problems
            ast.py        # Abstract Syntax Tree code; used in parsing
            ast_walker.py # used by transformers and generators to traverse ASTs
            constants.py  # constants
            generator.py  # the code to produce SMT-LIB 2.0/2.5 from ASTs
            parser.py     # a recursive descent parser for SMT-LIB 2.0/2.5
            scanner.py    # a lexical scanner for SMT-LIB
            smt.py        # convenience functions to produce SMT-LIB nodes
            types.py      # a legacy implementation of an AST type checker
            util.py       # utility functions
        tests/

The most interesting parts of the fuzzer are in the generators/ and
transformers/ directories. Some interesting things to look at are:

# generators/equality.py and generators/overlaps.py

They generate interesting and scaling inputs, but the code to do so is simple
and intuitive. This is due to the simplicity of AST representation as lists
of nodes, and also because all language-specific boilerplate functionality
has been factored out into generator.py.

# transformers/multiply.py

The code in this transformer is extremely succinct, describing only the
transformation. Future transformers can be easily added the same way.

Solvers
=======

The solvers have been pre-compiled and installed on the VM, in solvers/bin.
Building them on the VM takes a while (up to 2 hours), so we did this
beforehand. Nonetheless, they can be reinstalled by running:

    ./bin/install_solvers

NOTE: Z3str2 did not manage to build on the VM, and we abandonded efforts to
build it here. We did however still run it successfully for the experiments
we presented in the paper.

Experiments
===========

The experimental data (results and graphs) are all located in the experiments/
directory. The sample experiments have been pre-run, and can be run again. The
following command will recreate the results and graphs in the
sample-experiments/ directory:

    ./bin/run_sample_experiments

This command runs all the solvers on the experimental instances (from
instances/concats-small), and then generates the graphs
(in sample-experiments/graphs) from the experimental results
(in sample-experiments/results). To run an experiment on another suite
(say, regex-pair), you may run the following command:

    ./bin/run_one_experiment ./instances ./sample-experiments regex-pair

We created the sample directory because the full experiments usually take
many hours to run. Nonetheless, to run the full experiments (the results of
which will be in experiments/), run this command:

    ./bin/run_all_experiments
