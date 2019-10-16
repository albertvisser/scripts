#! /usr/bin/env python3
import os
import sys
from lxml import etree


def prettify(fname):
    newname = '_pretty'.join(os.path.splitext(fname))
    etree.parse(fname).write(newname, pretty_print=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python(3) xmlp.py <filename>")
    else:
        prettify(sys.argv[1])
