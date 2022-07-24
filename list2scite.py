#! /usr/bin/env python
"""open multiple files in one instance of SciTE
"""
import sys
import subprocess


def main(fname):
    cmd = ['SciTE']
    with open(fname) as f_in:
        for line in f_in:
            cmd.append(line.strip())
    subprocess.run(cmd)


if __name__ == '__main__':
    main(sys.argv[1])
