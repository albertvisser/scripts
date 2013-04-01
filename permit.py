#! /usr/bin/env/ python
"""
IIRC: fix file permissions after copying from Windows

nice to have: also fix line endings
"""
import sys
import os
import subprocess as sp

def main(path):
    path = os.path.abspath(path)
    for file in os.listdir(path):
        fullname = os.path.join(path, file)
        if os.path.isfile(fullname):
            rc = sp.call(['chmod', '644', fullname])
            if rc != 0:
                print 'chmod failed on file {}'.format(fullname)
        elif os.path.isdir(fullname):
            rc = sp.call(['chmod', '777', fullname])
            if rc != 0:
                print 'chmod failed on directory {}'.format(fullname)
            else:
                main(fullname)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        main(os.getcwd())
    elif len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print 'too many arguments, need only directory'
