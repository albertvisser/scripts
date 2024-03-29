#! /usr/bin/env python3
""" programmatically change directory names from a list produced using Double Commander

input: a file with file or directory names
"""
import sys
import pathlib


def main(temp_file):
    """rename from e.g. "Albert Visser" to "Visser, Albert"
    """
    with open(temp_file) as _in:
        data = _in.readlines()
    ## result = []
    for line in data:
        if ' ' not in line.strip():
            continue
        path = pathlib.Path(line.strip())
        root = path.parent
        first, last = path.name.rsplit(' ', 1)
        newpath = root / f'{last}, {first}'
        path.rename(newpath)


if __name__ == '__main__':
    main(sys.argv[1])
