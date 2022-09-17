#! /usr/bin/env python3
"""sort a given (text) file, line by line, alphabetically

depending on the value of the "output" parameter, the resulting file is either saved
in the same directory as the original (with the addition "_sorted") or as the given filename
added a line position other than the first to start sorting on
"""
import sys
import argparse
import os


def sort(fn, fnew, col):
    with open(fn) as _in:
        regels = _in.readlines()
    if col:
        regels.sort(key=lambda x: x[int(col):])
    else:
        regels.sort()
    with open(fnew, "w") as _out:
        for x in regels:
            _out.write(x)


def main(args):
    "check and execute"
    fn = args.file
    if not fn:
        fn = input("Geef naam van te sorteren file op: ")
    fnew = args.output
    if not fnew:
        fnew = '_sorted'.join(os.path.splitext(fn))
    col = args.column
    sort(fn, fnew, col)
    print("klaar, output in", fnew)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Simple file sorting program")
    parser.add_argument('file', help="Name of file to sort")
    parser.add_argument('-c', "--column", help="Column from which to start sorting")
    parser.add_argument('-o', '--output', help=("output filename (default is adding '-sorted' to"
                                                " the input filename"))
    args = parser.parse_args()
    main(args)
