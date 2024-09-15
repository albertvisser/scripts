"""Backend routines for a CSV helper

To facilitate editing a csv file, reformat it so all the fields have the same width
To the unsuspecting user who doesn't take precautions, a spreadsheet program usually
rounds off big numbers, strips leading zeroes and possibly transforms dates which
makes it hard to write it back in a usable state.
Here we just leave it in text mode and shrink the columns back before writing.
"""
import os
import csv


def expand(filename, outfile='', sep=';', quot='"'):
    """build new csv with same-length columns
    """
    formatted = outfile or filename
    # read in data
    with open(filename) as f_in:
        data = f_in.readlines()
    lengths = []
    rowdata = []
    # parse and determine column widths
    reader = csv.reader(data, delimiter=sep, quotechar=quot)
    for row in reader:
        rowdata.append(row)
        for ix, column in enumerate(row):
            if ix >= len(lengths):
                lengths.append(len(column))
            else:
                if len(column) > lengths[ix]:
                    lengths[ix] = len(column)
    # adjust column values
    newdata = []
    for row in rowdata:
        line = []
        for ix, column in enumerate(row):
            line.append(column.ljust(lengths[ix]))
        newdata.append(line)
    # write back
    with open(formatted, 'w') as f_out:
        writer = csv.writer(f_out, delimiter=sep, quotechar=quot, lineterminator=os.linesep)
        for row in newdata:
            writer.writerow(row)


def contract(filename, outfile='', sep=';', quot='"'):
    """build new csv with truncated columns
    """
    formatted = filename
    reformatted = outfile or formatted
    # read in data
    rowdata = []
    with open(formatted) as f_in:
        reader = csv.reader(f_in, delimiter=sep, quotechar=quot)
        for row in reader:
            rowdata.append(row)
    # truncate column values
    newdata = []
    for row in rowdata:
        line = []
        for column in row:
            line.append(column.rstrip())
        newdata.append(line)
    # write back
    with open(reformatted, 'w') as f_out:
        writer = csv.writer(f_out, delimiter=sep, quotechar=quot, lineterminator=os.linesep)
        for row in newdata:
            writer.writerow(row)
