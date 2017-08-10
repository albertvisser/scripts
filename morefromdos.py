#! /usr/bin/env python
"""converts all files in a directory from dos (crlf) to linux (lf) line-endings

optionally select only files with a certain extension
"""
import sys
import os
import subprocess as sp


def fromdos(path, cmp_ext='.py'):
    """apply program "fromdos" to multiple files in a directory
    """
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
