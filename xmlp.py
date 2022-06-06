#! /usr/bin/env python3
import os
import sys
from lxml import etree


def main(args):
    if len(args) != 2:
        print("usage: python(3) xmlp.py <filename>")
    else:
        fname = args[1]
        newname = '_pretty'.join(os.path.splitext(fname))
        etree.parse(fname).write(newname, pretty_print=True)


if __name__ == "__main__":
    main(sys.argv)
