#! /usr/bin/env python3
"""dosomethingwith.py

input: a file with file or directory names
initially written to programmatically change directory names from a list
produced using Double Commander

copy, rename and adapt the below function(s) to suit your needs
"""
import sys
import pathlib


def reorder_names(temp_file):
    """rename from e.g. "Albert Visser" to "Visser, Albert"
    """
    with open(temp_file) as _in:
        data = _in.readlines()
    ## result = []
    for line in data:
        path = pathlib.Path(line.strip())
        root = path.parent
        first, last = path.name.rsplit(' ', 1)
        newpath = root / ', '.join((last, first))
        path.rename(newpath)

reorder_names(sys.argv[1])
