#!/usr/bin/env python3

import sys
import os
import tempfile
import json
import argparse

# constants
LABEL_FONTSIZE     = 10
TITLE_FONTSIZE     = 14
SUBTITLE_FONTSIZE  = 10
DEFAULT_AXIS_LIMIT = 10
AXIS_MIN           = 0

NO_TITLE_BY_DEFAULT = False

DESCRIPTION = '''
Make a comparison plot from two datasets and print it in PNG format on stdout.

dataset format:
  [
      {
          "problem": "/path/to/problem",
          "result":  "sat"|"unsat"|"unknown"|"timeout"|"error",
          "solver":  "solver name",
          "elapsed": 1.0 // time it took, as a float
      },
      ...
  ]
'''

MARKERS = [
    4,
    5,
    6,
    7,
    8
]

# helpers
def plottable(row):
    return (
        row['result'] == 'sat' or
        row['result'] == 'unsat' or
        row['result'] == 'timeout'
    )

def get_solver_name(dataset):
    return dataset[0]['solver']

def get_i(data, i):
    return [d[i] for d in data]

def data2png(x, x_name, y, y_name, title):

    # configure plot library to use SVG
    import matplotlib
    matplotlib.use('svg')
    import matplotlib.pyplot as pyplot

    # set title
    if title is not None:
        pyplot.suptitle(title + '\n', fontsize=TITLE_FONTSIZE)

    # combine data
    points     = []
    num_better = 0
    num_worse  = 0
    for x_row, y_row in zip(x, y):

        x_value = x_row['elapsed']
        y_value = y_row['elapsed']

        # only look at plottable runs
        if plottable(x_row) and plottable(y_row):

            # record performance
            if x_value <= y_value:
                num_better += 1
            else:
                num_worse += 1

            # save the point
            points.append((x_row['elapsed'], y_row['elapsed']))

    # get total number of runs and build subtitle
    num_total = num_better + num_worse
    if num_total > 0:

        # measure performance
        subtitle = '''{x} was better {b}/{t} times ({bp:.2f} %), worse {w}/{t} times ({wp:.2f} %)'''.format(
            x  = x_name,
            b  = num_better,
            w  = num_worse,
            t  = num_total,
            bp = (num_better / num_total) * 100.0,
            wp = (num_worse / num_total) * 100.0
        )

    else:
        subtitle = '''not enough data to determine which was better'''

    # set subtitle
    pyplot.title(subtitle, fontsize=SUBTITLE_FONTSIZE)

    # set axis labels
    pyplot.xlabel('{} time (s)'.format(x_name), fontsize=LABEL_FONTSIZE)
    pyplot.ylabel('{} time (s)'.format(y_name), fontsize=LABEL_FONTSIZE, labelpad=12)

    x_values = get_i(points, 0)
    y_values = get_i(points, 1)

    # determine axis limits
    # NOTE: this needs to be a square plot, so the axes have the same limits
    if len(points) == 0:
        min_x = AXIS_MIN
        max_x = DEFAULT_AXIS_LIMIT
        min_y = AXIS_MIN
        max_y = DEFAULT_AXIS_LIMIT
    else:
        min_x = AXIS_MIN
        max_x = max(max(x_values), max(y_values))
        min_y = AXIS_MIN
        max_y = max_x

    # set axis limits
    pyplot.axis([min_x, max_x, min_y, max_y])

    # create the graph
    pyplot.scatter(x_values, y_values, marker='o', alpha=0.3)

    # draw the 45-degree line
    pyplot.plot([min_x, max_x], [min_y, max_y], 'r-')

    # adjust plot spacing to fit the data
    pyplot.autoscale(tight=False)

    # make a temporary file to store the graph
    # FIXME:
    #       this is here because I don't know how to make pyplot
    #       print the graph to something other than a file
    # NOTE:
    #      doing an instant close() of the file because pyplot will open it
    #      on its own, and will close it on its own, after which we will
    #      manually open it on our own
    fd, path = tempfile.mkstemp(suffix='.png')
    os.close(fd)

    # save the graph
    pyplot.savefig(path)

    # read the graph back
    with open(path, 'rb') as graph_file:
        png = graph_file.read()

    return png

def main():

    # create arg parser
    parser = argparse.ArgumentParser(
        description     = DESCRIPTION,
        formatter_class = argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        'name',
        type = str,
        help = 'name of the experiment (used in the title)'
    )
    parser.add_argument(
        'a',
        type    = argparse.FileType('r'),
        help    = 'dataset for solver A'
    )
    parser.add_argument(
        'b',
        type    = argparse.FileType('r'),
        help    = 'dataset for solver B'
    )
    parser.add_argument(
        '--no-title',
        '-n',
        dest    = 'no_title',
        action  = 'store_true',
        default = NO_TITLE_BY_DEFAULT,
        help    = 'don\'t give the graph a title (default: {})'.format(NO_TITLE_BY_DEFAULT)
    )

    # parse args
    args = parser.parse_args()

    # read in data
    a_data = json.loads(args.a.read())
    b_data = json.loads(args.b.read())

    # error out on empty data
    if len(a_data) == 0 or len(b_data) == 0:
        print('ERROR: no data', file=sys.stderr)
        return

    # make names
    a_name = get_solver_name(a_data)
    b_name = get_solver_name(b_data)

    # make title
    if args.no_title is False:
        title = '{}: {} vs {}'.format(args.name, a_name, b_name)
    else:
        title = None

    # print PNG image
    sys.stdout.buffer.write(data2png(a_data, a_name, b_data, b_name, title))

if __name__ == '__main__':
    main()
