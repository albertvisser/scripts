#! /usr/bin/env python3

import os
import sys
from lxml import etree

def prettify(fname):
    data = etree.parse(fname)
    with open('_pretty'.join(os.path.splitext(fname)), 'w') as _out:
        print(str(etree.tostring(data, pretty_print=True), encoding='utf8'), file=_out)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python(3) xmlp.py <filename>")
    else:
        prettify(sys.argv[1])
