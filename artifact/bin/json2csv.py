#!/usr/bin/env python3

import sys
import json
import argparse

DESCRIPTION = '''
Read JSON object list on stdin and print it as CSV on stdout.

notes:
  the first object's keys are used for the CSV header

example:
  [                        x,y
    {"y": 0, "x": 0},  ->  0,0
    {"y": 2, "x": 1}       1,2
  ]
'''

def main():

    # create arg parser
    parser = argparse.ArgumentParser(
        description     = DESCRIPTION,
        formatter_class = argparse.RawTextHelpFormatter
    )

    # parse args
    args = parser.parse_args()

    # read in JSON list
    dicts = json.loads(sys.stdin.read())

    # get objects keys
    # NOTE:
    #      it's assumed that all objects have the same keys
    keys = sorted(dicts[0].keys())

    # print keys as CSV header
    print(','.join(keys))

    # print each object's values as CSV rows
    for d in dicts:
        print(','.join(map(str, [d[k] for k in keys])))

if __name__ == '__main__':
    main()
