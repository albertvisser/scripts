#! /usr/bin/env python3

"""pretty-print json data in a given file

saves a pretty-printed version instead of overwriting the original
"""
import sys
import os
import json

INDENT = 2


def main(args):
    if len(args) != 2:
        print("usage: python(3) jsonp.py <filename>")
        return
    filename = args[1]
    outname = '_pretty'.join(os.path.splitext(filename))
    with open(filename) as _in:
        data = json.load(_in)
    with open(outname, "w") as _out:
        json.dump(data, _out, indent=INDENT)


if __name__ == "__main__":
    main(sys.argv)
