#! /usr/bin/env python3
"""open multiple files in one instance of VI
"""
import sys
import subprocess

def main(fname):
    with open(fname) as f_in:
        files = [x.strip() for x in f_in]
    command = ["gnome-terminal", "--profile", 'Code Editor Shell', "--", "vim"] + files
    subprocess.run(command)

if __name__ == '__main__':
    main(sys.argv[1])
