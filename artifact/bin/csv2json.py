#!/usr/bin/env python3

import sys
import json
import csv
import argparse

DESCRIPTION = '''
Read CSV file on stdin and print it as JSON on stdout.

example:
  x,y      [
  0,0  ->    {"y": 0, "x": 0},
  1,2        {"y": 2, "x": 1}
           ]
'''

def str2value(v):
    try:
        return int(v)
    except ValueError as e:
        pass
    try:
        return float(v)
    except ValueError as e:
        pass
    return v

def make_dict(keys, values):
    values = map(str2value, values)
    return dict(zip(keys, values))

def main():

    # create arg parser
    parser = argparse.ArgumentParser(
        description     = DESCRIPTION,
        formatter_class = argparse.RawTextHelpFormatter
    )

    # parse args
    args = parser.parse_args()

    # create CSV reader for all lines
    # NOTE:
    #      csv.reader returns a generator of rows, which are string tuples
    rows = csv.reader(sys.stdin, delimiter=',', quotechar='\'')

    # interpret the first tuple as the header
    header = next(rows)

    # create a list of dicts by mapping the header to each row
    dicts = [make_dict(header, row) for row in rows]

    # dump the list as json
    print(json.dumps(dicts))

if __name__ == '__main__':
    main()
