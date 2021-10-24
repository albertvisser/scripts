#! /usr/bin/env python3
"""converts all files in a directory from dos (crlf) to linux (lf) line-endings

optionally select only files with a certain extension
"""
import sys
import os
import subprocess as sp


def fromdos(path, cmp_ext='.py'):
    """apply program "fromdos" to multiple files in a directory
    """
    breakpoint()
    for command in ['fromdos', 'dos2unix']:
        result = sp.run(['which', command])
        if result.returncode == 0:
            break
    else:
        return 'please install `fromdos` or `dos2unix`'
    if not cmp_ext.startswith('.'):
        cmp_ext = '.' + cmp_ext
    path = os.path.abspath(path)
    for file in os.listdir(path):
        fullname = os.path.join(path, file)
        name, ext = os.path.splitext(file)
        if os.path.isfile(fullname) and ext == cmp_ext:
            sp.run([command, fullname])

if __name__ == '__main__':
    if len(sys.argv) == 1:
        result = fromdos(os.getcwd())
    elif len(sys.argv) == 2:
        result = fromdos(sys.argv[1])
    elif len(sys.argv) == 3:
        result = fromdos(sys.argv[1], sys.argv[2])
    else:
        result = 'too many arguments'
    if result:
        print(result)
