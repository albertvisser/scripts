#! /usr/bin/env python
"""creates a temporary file, loads expanded json into it  then opens it for viewing

developed for Double Commander
"""
import sys
import os.path
import tempfile
import subprocess
import jsonvp


def main(args):
    "do the thing"
    filename = jsonvp.check_usage(args, 'jsonv')
    if filename:
        data = jsonvp.read_json(filename)
        tmp_file, tmp_name = tempfile.mkstemp(suffix='.json')
        jsonvp.dump_json(tmp_file, data)
        title = os.path.basename(filename)
        subprocess.run(['gnome-terminal', '--geometry=102x54', '--', 'vim', '-R', tmp_name, '-c',
                        f'set titlestring=[...]/{title}', '-c', 'set foldmethod=syntax'])


if __name__ == "__main__":
    main(sys.argv)
