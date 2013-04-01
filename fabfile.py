import os
import datetime
from fabric.api import local, sudo
"""collection of shortcut functions for common tasks like

. installing a new version of SciTE
. archiving a predefined set of files
. managing mongodb (start/stop/restart server and repair)
. copying a file from the local to the webserver www directory
. helper functions for (py)gettext internationalization
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

def arcstuff(*names):
    """backup selected files indicated in a .conf file

    if no name(s) provided, select all arcstuff config files present
    """
    if not names:
        files = [x for x in os.listdir(os.path.dirname(__file__))
            if x.startswith('arcstuff') and os.path.splitext(x)[1] == '.conf']
        names = []
        for x in files:
            y = os.path.splitext(x)[0]
            z = '' if '_' not in y else y.split('_')[1]
            names.append(z)
    else:
        files = []
        for name in names:
            hlp = '_' + name if name else ''
            fname = 'arcstuff{}.conf'.format(hlp)
            if not os.path.exists(fname):
                raise ValueError('abort: no config file for {} ({} does not exist'
                    ')'.format(name, fname))
            files.append(fname)
    for indx, infile in enumerate(files):
        name = 'all' if not names[indx] else names[indx]
        dts = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
        outfile = '/home/albert/arcstuff/{}_{}.tar.gz'.format(name, dts)
        with open(infile) as f_in:
            first = True
            command = 'tar -czvf {}'.format(outfile)
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

def start_mongo():
    "start mongo database server"
    local('sudo service mongodb start')

def stop_mongo():
    "stop mongo database server"
    local('sudo service mongodb stop')

def restart_mongo():
    "restart mongo db"
    local('sudo service mongodb restart')

def repair_mongo():
    "repair mongo db"
    local('sudo rm /var/lib/mongodb/mongodb.lock')
    local('sudo mongod --dbpath /var/lib/mongodb/ --repair')
    local('sudo chmod 777 /var/lib/mongodb')

def wwwcopy(name):
    "copy indicated file from ~/www to /var/www"
    local('sudo cp ~/www/nginx-root/{0} /var/www/{0}'.format(name))

def gettext(sourcefile):
    """internalization: gather strings from file

    verzamel gemarkeerde symbolen in het aangegeven source file
    en schrijf ze weg in een bestand genaamd messages.pot
    """
    local("pygettext {}".format(sourcefile))

def poedit(language_code):
    """internalization: edit translations in language file

    bewerkt het aangegeven language file met poedit
    """
    fnaam = "{}.po".format(language_code)
    if not os.path.exists(fnaam):
        local('poedit')
    else:
        local("poedit {}".format(fnaam))

def place(language_code, appname, locatie=""):
    """internalization: make translation usable

    plaats het gecompileerde language file zodat het gebruikt kan worden
    gebruik <locatie> als de locale directory niet direct onder de huidige zit
    """
    loc = 'locale'
    if locatie:
        loc = os.path.join(locatie, loc)
    loc = os.path.abspath(loc)
    if not os.path.exists(loc):
        os.mkdir(loc)
    loc = os.path.join(loc, language_code)
    if not os.path.exists(loc):
        os.mkdir(loc)
    loc = os.path.join(loc, 'LC_MESSAGES')
    if not os.path.exists(loc):
        os.mkdir(loc)
    local('msgfmt {}.po -o {}'.format(language_code, os.path.join(loc,
        appname + '.mo')))
