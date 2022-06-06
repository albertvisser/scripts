#! /usr/bin/env python3
"""sort a given (text) file, line by line, alphabetically

depending on the value of the second parameter, the resulting file is either saved
in the same directory as the original (with the suffix "sorted") or in the system's
temporary directory
"""
import sys
import os
TMP = '/tmp'
if sys.platform.startswith('win'):
    TMP = "C:\\Windows\\Tmp"


def sort(fn, tmp=False):
    """sorting the lines of the file and write the result to a new file"""
    if tmp:
        fnew = os.path.join(TMP, os.path.basename(fn))
    else:
        fnew = '_sorted'.join(os.path.splitext(fn))
    with open(fn) as _in, open(fnew, "w") as _out:
        regels = _in.readlines()
        regels.sort()
        for x in regels:
            _out.write(x)
    return fnew


def main(args):
    "check and execute"
    if len(args) > 1:
        fn = sort(args[1])
    else:
        fn = sort(input("Geef naam van te sorteren file op: "))
    print("klaar, output in", fn)


if __name__ == '__main__':
    main(sys.argv)
