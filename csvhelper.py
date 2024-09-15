#! /usr/bin/env python3

"""Frontend for CSV helper

Simplest form: a command line utility reading and writing files
possibly could take an extra parameter specifying minimum widths for columns
"""
import argparse
import textwrap
import shutil
import format_csv as fmt
actiondict = {'E': fmt.expand, 'T': fmt.contract}

parser = argparse.ArgumentParser(description='CSV editing helper',
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=textwrap.dedent("""\
        E(xpand) means extending the columns to equal width among rows
        T(runcate) means shrinking the column widths by removing trailing spaces
        """))
parser.add_argument('filename', help='input filename')
parser.add_argument('-o', '--outfile',
                    help='output filename if different from input')
parser.add_argument('-b', '--backup', action='store_true',
                    help='backup input file (when overwriting)')
parser.add_argument('-s', '--sep', help='field separator if different from ,')
parser.add_argument('-q', '--quot', help='quote character if different from "')
parser.add_argument('action', choices='ET', help='action to perform on the file')

args = parser.parse_args()
sep = args.sep or ','
quot = args.quot or '"'
if args.backup:
    shutil.copyfile(args.filename, args.filename + '~')
actiondict[args.action](args.filename, args.outfile, sep, quot)
