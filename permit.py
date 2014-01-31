#! /usr/bin/env/ python
"""
fix directory and file permissions after copying from Windows

nice to have: also fix line endings
"""
import sys
import os
import subprocess as sp

def main(path, do_files=True):
    path = os.path.abspath(path)
    for file in os.listdir(path):
        fullname = os.path.join(path, file)
        if os.path.isfile(fullname) and do_files:
            rc = sp.call(['chmod', '644', fullname])
            if rc != 0:
                print 'chmod failed on file {}'.format(fullname)
        elif os.path.isdir(fullname):
            rc = sp.call(['chmod', '755', fullname])
            if rc != 0:
                print 'chmod failed on directory {}'.format(fullname)
            else:
                main(fullname)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        main(os.getcwd())
    elif len(sys.argv) == 2:
        main(sys.argv[1])
    elif len(sys.argv) == 3:
        main(sys.argv[1], do_files=False)
    else:
        print """\
usage: [python3] permit.py [directory-name] [do-not-process-files]

do-not-process-file can be anything non-empty
"""
