# sort and compare
import sys
import os
import sort_file
import subprocess

usage = """\
usage: python(3) sort_and_compare.py <filename_1> <filename_2>

takes two (text) files, sorts each one line by line and then compares them
"""

def main(args):
    if len(args) != 2:
        print(usage)
        return
    for ix, name in enumerate(args):
        if not os.path.exists(name):
            print("file {} does not exist".format(ix))
            return
    sorted_1 = sort_file.main(args[0], tmp=True)
    sorted_2 = sort_file.main(args[1], tmp=True)
    subprocess.call(['kdiff3', sorted_1, sorted_2])
    ## os.remove(sorted_1)
    ## os.remove(sorted_2)

if __name__ == '__main__':
    main(sys.argv[1:])
