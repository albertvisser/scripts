#! /usr/bin/env python
import sys
import os
import subprocess as sp

def fromdos(path, cmp_ext='.py'):
    path = os.path.abspath(path)
    for file in os.listdir(path):
        fullname = os.path.join(path, file)
        name, ext = os.path.splitext(file)
        if os.path.isfile(fullname) and ext == cmp_ext:
            rc = sp.call(['fromdos', fullname])
            if rc != 0:
                print('fromdos {} failed!'.format(fullname))

if __name__ == '__main__':
    if len(sys.argv) == 1:
        fromdos(os.getcwd())
    elif len(sys.argv) == 2:
        fromdos(sys.argv[1])
    elif len(sys.argv) == 3:
        fromdos(sys.argv[1], sys.argv[2])
    else:
        print('too many arguments')
