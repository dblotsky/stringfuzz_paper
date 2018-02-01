#!/usr/bin/env python3

import os
import sys
import json
import subprocess
import signal
import datetime
import argparse

from collections import namedtuple

# constants
SAT_RESULT     = 'sat'
UNSAT_RESULT   = 'unsat'
UNKNOWN_RESULT = 'unknown'
TIMEOUT_RESULT = 'timeout'
ERROR_RESULT   = 'error'

DEFAULT_TIMEOUT = 15.0

CSV  = 'csv'
JSON = 'json'

OUTPUT_FORMATS = [CSV, JSON]

# data
Result = namedtuple('Result', ('solver', 'problem', 'elapsed', 'result', 'command'))

# helpers
def output2result(output):
    # NOTE:
    #      it's important to check for unsat first, since sat
    #      is a substring of unsat
    if 'UNSAT' in output or 'unsat' in output:
        return UNSAT_RESULT
    if 'SAT' in output or 'sat' in output:
        return SAT_RESULT
    if 'UNKNOWN' in output or 'unknown' in output:
        return UNKNOWN_RESULT

    print('couldn\'t parse output: \'' + output + '\'', file=sys.stderr)
    return ERROR_RESULT

def run_problem(solver, invocation, problem, timeout, verbose, debug):

    # pass the problem to the command
    command = invocation + problem

    # print command that will be run
    if verbose is True or debug is True:
        print('RUNNING:', repr(command), file=sys.stderr)

    # get start time
    start = datetime.datetime.now().timestamp()

    # run command
    process = subprocess.Popen(
        command,
        shell      = True,
        stdout     = subprocess.PIPE,
        stderr     = subprocess.PIPE,
        preexec_fn = os.setsid
    )

    # wait for it to complete
    try:
        process.wait(timeout=timeout)

    # if it times out ...
    except subprocess.TimeoutExpired as e:

        # kill it
        print('TIMED OUT:', repr(command), '... killing', process.pid, file=sys.stderr)
        os.killpg(os.getpgid(process.pid), signal.SIGINT)

        # set timeout result
        elapsed = timeout
        result  = TIMEOUT_RESULT

    # if it completes in time ...
    else:

        # measure run time
        end     = datetime.datetime.now().timestamp()
        elapsed = end - start

        # get result
        stdout = process.stdout.read().decode('utf-8')
        stderr = process.stderr.read().decode('utf-8')
        result = output2result(stdout + stderr)

        # print output
        if debug is True:
            print('STDOUT:', file=sys.stderr)
            print(stdout, file=sys.stderr)
            print('STDERR:', file=sys.stderr)
            print(stderr, file=sys.stderr)

    # make result
    result = Result(
        command = invocation + 'PROBLEM',
        solver  = solver,
        problem = problem,
        elapsed = elapsed,
        result  = result
    )

    return result

def main():

    # create arg parser
    parser = argparse.ArgumentParser(description='Run a solver on problem instances.')
    parser.add_argument(
        'solver',
        type = str,
        help = 'solver name'
    )
    parser.add_argument(
        'command',
        type = str,
        help = 'command to run the solver'
    )
    parser.add_argument(
        '--timeout',
        '-t',
        dest    = 'timeout',
        type    = float,
        default = DEFAULT_TIMEOUT,
        help    = 'timeout, in seconds'
    )
    parser.add_argument(
        '--format',
        '-f',
        dest    = 'format',
        type    = str,
        choices = OUTPUT_FORMATS,
        default = CSV,
        help    = 'output format'
    )
    parser.add_argument(
        '--problem',
        '-p',
        dest   = 'problems',
        type   = str,
        action = 'append',
        help   = 'a problem instance'
    )
    parser.add_argument(
        '--problem-list',
        '-l',
        dest   = 'problem_lists',
        type   = str,
        action = 'append',
        help   = 'a list of problem instances'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        dest    = 'verbose',
        action  = 'store_true',
        default = False,
        help    = 'echo commands as they are run'
    )
    parser.add_argument(
        '--debug',
        '-d',
        dest    = 'debug',
        action  = 'store_true',
        default = False,
        help    = 'print output of runs'
    )

    # parse args
    args = parser.parse_args()

    # collect individual problems
    if args.problems is None:
        problems = []
    else:
        problems = args.problems

    # collect problems from problem lists
    if args.problem_lists is not None:
        for problem_list in args.problem_lists:

            # read in problems from file
            with open(problem_list, 'r') as problem_file:
                problems += problem_file.read().splitlines()

    # if no problems were passed in args, read them from stdin
    elif len(problems) < 1:
            for line in sys.stdin:
                problems += line

    # if no problems were collected by this point, exit
    if len(problems) < 1:
        exit(1)

    # run the problems
    results = []
    for problem in problems:
        result = run_problem(args.solver, args.command, problem.strip(), args.timeout, args.verbose, args.debug)
        results.append(result)

    # sanity check
    assert len(results) > 0

    # transform results (which are namedtuples) to dicts
    result_dicts = [r._asdict() for r in results]

    # print results
    if args.format == CSV:

        # print header
        keys = sorted(result_dicts[0].keys())
        print(','.join(keys))

        # print rows
        for result in result_dicts:
            print(','.join(map(repr, [result[k] for k in keys])))

    elif args.format == JSON:

        # print straight from JSON serialiser
        print(json.dumps(result_dicts))

if __name__ == '__main__':
    main()
