# -*- coding: utf-8 -*-
import os
import sys
import xml.etree.ElementTree as et

usage = """\
usage: python sortxml.py filename attribute_name

filename is the name of an existing xml file
attribute_name is the name of an attribute that all the elements
  directly under the root have in common
"""

def write_sorted(filename, attrname):
    root = et.ElementTree(file=filename).getroot()
    newroot = sort_tree(root, attrname)
    newfile = '_sorted'.join(os.path.splitext(filename))
    et.ElementTree(newroot).write(newfile, method="xml")

def sort_tree(root, attrname):
    ## filename = os.path.abspath(filename)
    list_to_order = []
    for element in list(root):
        attrval = element.get(attrname)
        list_to_order.append((attrval, element))
    list_to_order.sort()
    newroot = et.Element(root.tag)
    for attrval, element in list_to_order:
        newroot.append(element)
    return newroot

if __name__ == "__main__":
    if len(sys.argv) == 3:
        sort_tree(*sys.argv[1:])
    else:
        sys.stdout.write(usage)
