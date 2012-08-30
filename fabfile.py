import os
import datetime
from fabric.api import local, sudo
"""collection of shortcut functions for common tasks like

. installing a new version of SciTE
"""

def install_scite(version):
    """upgrade SciTE. argument: version number as used in filename
    """
    filename = os.path.abspath('Downloads/SciTE/gscite{}.tgz'.format(version))
    if not os.path.exists(filename):
        print('{} does not exist'.format(filename))
        return
    local('tar -zxf {}'.format(filename))
    local('sudo cp gscite/SciTE /usr/bin')
    local('sudo cp gscite/*.properties /usr/share/scite')
    local('sudo cp gscite/*.html /usr/share/scite')
    local('sudo cp gscite/*.png /usr/share/scite')
    local('sudo cp gscite/*.jpg /usr/share/scite')
    local('rm gscite -r')

def arcstuff():
    """backup selected files indicated in an ini file
    """
    infile = 'arcstuff.ini'
    outfile = datetime.datetime.today().strftime('/home/albert/backup_%Y%m%d%H%M%S'
        '.tar.gz')
    with open(infile) as f_in:
        first = True
        command = 'tar -cIvf {}'.format(outfile)
        prepend = ''
        for line in f_in:
            line = line.strip()
            if line.startswith('['):
                if line.endswith(']'):
                    prepend = line[1:-1]
                continue
            if not line or line.startswith('#'):
                continue
            try:
                line, rest = line.split('#', 1)
            except ValueError:
                pass
            path = os.path.join(prepend, line) if prepend else line
            command = '{} {}'.format(command, path.strip())
    local(command)
