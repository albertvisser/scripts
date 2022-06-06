#! /usr/bin/env python3
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


if __name__ == 'main':
    main(sys.argv[1])
