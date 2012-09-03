#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

def main(fn):
    h = os.path.splitext(fn)
    fnew = '_sorted'.join(h)
    f = open(fn)
    regels = f.readlines()
    f.close()
    regels.sort()
    f = open(fnew,"w")
    for x in regels:
        f.write(x)
    f.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main("x.txt")
