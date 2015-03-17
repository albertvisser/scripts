#! /usr/bin/env python3
# -*- coding: utf-8 -*-
print('start')
import sys
import os

def main(fn):
    fnew = '_sorted'.join(os.path.splitext(fn))
    with open(fn) as _in, open(fnew, "w") as _out:
        regels = _in.readlines()
        regels.sort()
        for x in regels:
            _out.write(x)
    return fnew

if __name__ == '__main__':
    print(sys.argv)
    if len(sys.argv) > 1:
        fn = main(sys.argv[1])
    else:
        fn = main(input("Geef naam van te sorteren file op: "))
    print("klaar, output in", fn)
