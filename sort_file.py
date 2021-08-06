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
    TMP = "C:\\Windows\\Temp"


def main(fn, tmp=False):
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

if __name__ == '__main__':
    print(sys.argv)
    if len(sys.argv) > 1:
        fn = main(sys.argv[1])
    else:
        fn = main(input("Geef naam van te sorteren file op: "))
    print("klaar, output in", fn)
