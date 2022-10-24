#! /usr/bin/env python3
"""converts all files in a directory from dos (crlf) to linux (lf) line-endings

optionally select files with a extension different from '.py'
"""
import sys
import os
import subprocess as sp


def fromdos(path, cmp_ext='.py'):
    """apply program "fromdos" to multiple files in a directory
    """
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
        if os.path.isfile(fullname) and (ext == cmp_ext or (cmp_ext == '.' and ext == '')):
            sp.run([command, fullname])


def main(args):
    "read args and execute"
    if len(args) == 1:
        result = fromdos(os.getcwd())
    elif len(args) == 2:
        result = fromdos(args[1])
    elif len(args) == 3:
        result = fromdos(args[1], args[2])
    else:
        result = 'too many arguments'
    if result:
        print(result)


if __name__ == '__main__':
    main(sys.argv)
