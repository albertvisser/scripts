#! /usr/bin/env python3
"""pretty-print json data in a given file

saves a pretty-printed version instead of overwriting the original
"""
import sys
import os.path
import jsonvp


def main(args):
    "do the thing"
    filename = jsonvp.check_usage(args, 'jsonp')
    if filename:
        data = jsonvp.read_json(filename)
        outname = '_pretty'.join(os.path.splitext(filename))
        jsonvp.dump_json(outname, data)


if __name__ == "__main__":
    main(sys.argv)
