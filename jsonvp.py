#! /usr/bin/env python
"""creates a temporary file, loads expanded json into it  then opens it for viewing

developed for Double Commander
"""

import json5 as json


def check_usage(args, toolname):
    """error on less or more than one argument; translate "escaped spaces" to simple ones
    """
    if len(args) != 2:
        print(f"usage: python {toolname} <filename>")
        return
    filename = args[1]
    if "\\ " in filename:
        filename = filename.replace("\\ ", " ")    # Double Commander tries to escape spaces
    return filename


def read_json(filename):
    "read json from a file"
    # try:
    with open(filename, encoding='utf-8') as _in:
        data = json.load(_in)
    # except JSONDecodeError as exc:  # niet nodig met json5
    #     subprocess.run(['zenity', '--error', f'--text={exc}'])
    #     return
    return data


def dump_json(outfile, data, filename=''):
    "output json to a file"
    with open(outfile, 'w', encoding='utf-8') as _out:
        json.dump(data, _out, indent=4)
