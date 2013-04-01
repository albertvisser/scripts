import os
import sys
import stat
"""
Permissies in een directory tree op standaard waarden zetten
nadat de bestanden zijn gekopieerd vanaf een device
dat geen unix permits kan onthouden (zoals een mobiele harddisk)

uit te voeren in de root van de betreffende tree
"""

def doit(path):
    for entry in os.listdir(path):
        fnaam = os.path.join(path, entry)
        if os.path.isfile(fnaam):
            os.chmod(fnaam, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
        elif os.path.isdir(fnaam):
            os.chmod(fnaam, stat.S_IFDIR | stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            doit(fnaam)

if __name__ == "__main__":
    doit(os.getcwd())