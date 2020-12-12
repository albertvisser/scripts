"""import Invoke commands from various location as well as define some others
"""
import os
import os.path
import stat
import datetime
from invoke import task, Collection

import session
import repo
import tags
import www
import lang
import db


@task
def listbin(c):
    "list command files in scripts directory (~/bin) (based on readme file)"
    with open(os.path.expanduser('~/bin/readme.rst')) as _in:
        lines = _in.readlines()
    commands = {}
    lastcommand = get_starters = False
    command = ''
    starters = {}
    for line in lines:
        if line.startswith("Requirements"):
            lastcommand = True
            command = ''
        elif not lastcommand:
            if line.startswith('**'):
                command = line.strip()
                commands[command] = []
            elif command:
                commands[command].append(line.strip())
        elif line.startswith('symlinks'):
            get_starters = True
        elif get_starters:
            if line.startswith('**'):
                command = line.strip()
                starters[command] = []
            else:
                if command:
                    starters[command].append(line.strip())
    for x, y in commands.items():
        for command in ['.hgignore', 'arcstuff', 'settings', 'fabfile', 'readme']:
            if command in x:
                break
        else:
            print(x, ':', ' '.join(y))
    print()
    for x, y in starters.items():
        print(x, ':', ' '.join(y))


@task(help={'version': 'Version of sciTE to install'})
def install_scite(c, version):
    """upgrade SciTE. argument: version number as used in filename
    """
    filename = os.path.expanduser('~/Downloads/SciTE/gscite{}.tgz'.format(version))
    if not os.path.exists(filename):
        print('{} does not exist'.format(filename))
        return
    # with settings(hide('running', 'warnings'), warn_only=True):
    result = c.run('tar -zxf {}'.format(filename))
    if result.failed:
        result = c.run('tar -xf {}'.format(filename))
    c.run('sudo cp gscite/SciTE /usr/bin')
    c.run('sudo cp gscite/*.properties /etc/scite')  # /usr/share/scite')
    c.run('sudo cp gscite/*.html /usr/share/scite')
    c.run('sudo cp gscite/*.png /usr/share/scite')
    c.run('sudo cp gscite/*.jpg /usr/share/scite')
    c.run('rm gscite -r')


@task(help={'version': 'Version of sciTE to build'})
def build_scite(c, version):
    """(re)build SciTE. argument: version number as used in filename

    standard binary is 32-bit and my system is 64-bit, so I need this now
    """
    filename = os.path.expanduser('~/Downloads/SciTE/scite{}.tgz'.format(version))
    if not os.path.exists(filename):
        print('{} does not exist'.format(filename))
        return
    logfile = '/tmp/scite_build.log'
    with open(logfile, 'w') as _out:
        with c.cd('/tmp'):
            result = c.run('tar -zxf {}'.format(filename))
            # looks like he's not gzipping anymore, if so then try again
            if result.failed:
                c.run('tar -xf {}'.format(filename))
        with c.cd('/tmp/scintilla/gtk'):
            result = c.run('make')
        _out.write(result.stdout + "\n")
        if result.failed:
            err = 'make scintilla failed'
            _out.write(result.stderr + "\n")
        else:
            with c.cd('/tmp/scite/gtk'):
                err = ''
                result = c.run('make')
                _out.write(result.stdout + "\n")
                if result.failed:
                    err = 'make scite failed'
                    _out.write(result.stderr + "\n")
                else:
                    result = c.run('sudo make install')
                    _out.write(result.stdout + "\n")
                    if result.failed:
                        err = 'make install failed'
                        _out.write(result.stderr + "\n")
    if err:
        print('{}, see {}'.format(err, logfile))
    else:
        print('ready, see {}'.format(logfile))


@task(help={'names': 'list of files containing the files to backup'})
def arcstuff(c, names):
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
        for name in names.split(','):
            hlp = '_' + name if name else ''
            fname = 'arcstuff{}.conf'.format(hlp)
            if not os.path.exists(fname):
                raise ValueError('abort: no config file for {} '
                                 '({} does not exist)'.format(name, fname))
            files.append(fname)
    for indx, infile in enumerate(files):
        name = 'all' if not names[indx] else names[indx]
        dts = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
        outfile = os.path.expanduser('~/arcstuff/{}_{}.tar.gz'.format(name, dts))
        with open(infile) as f_in:
            ## first = True
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
        c.run(command)


@task(help={'path': 'root path on which the permissions need to be reset'})
def chmodrecursive(c, path=None):
    """
    Permissies in een directory tree op standaard waarden zetten
    bv. nadat de bestanden zijn gekopieerd vanaf een device
    dat geen unix permits kan onthouden (zoals een mobiele FAT-harddisk)

    eenvoudigst om uit te voeren in de root van de betreffende tree
    """
    if path is None:
        path = os.getcwd()
    for entry in os.listdir(path):
        if entry in ('__pycache__', '.hg'):
            continue
        fnaam = os.path.join(path, entry)
        if os.path.isfile(fnaam):
            try:
                os.chmod(fnaam, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
            except PermissionError:
                pass
        elif os.path.islink(fnaam):
            continue
        elif os.path.isdir(fnaam):
            try:
                os.chmod(fnaam, stat.S_IFDIR | stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            except PermissionError:
                pass
            else:
                chmodrecursive(c, fnaam)


@task
def create_shortcuts(c):
    """(re)build script shortcuts in bin directory
    """
    os.chdir(os.path.expanduser('~/bin'))
    data = (('/usr/share/vim/vim74/macros/less.sh', 'vless'),
            ('/home/albert/projects/albumsgui/start_gui.py', 'albumsgui'),
            ('/home/albert/projects/filefindr/start.py', 'afrift'),
            ('/home/albert/bin/ramble', 'diary'),
            ('/home/albert/projects/modreader/modreadergui.py', 'modreader'),
            ('/home/albert/projects/mylinter/lint-all', 'lint-all'),
            ('/home/albert/projects/hotkeys/start.py', 'hotkeys'),
            ('/home/albert/projects/rst2html/mdviewer.py', 'mdview'),
            ('/home/albert/projects/notetree/nt_start.py', 'notetree'),
            ('/home/albert/projects/xmledit/xmleditor.py', 'xmledit'),
            ('/home/albert/projects/cssedit/cssedit/start_editor.py', 'cssedit'),
            ('/home/albert/projects/htmledit/htmleditor.py', 'htmledit'),
            ('/home/albert/projects/doctree/dt_start.py', 'treedocs'),
            ('/home/albert/projects/notetree/nt2ext.py', 'nt2ext'),
            ('/home/albert/projects/apropos/apo_start.py', 'a-propos'),
            ('/home/albert/projects/probreg/pr_start.py', 'probreg'),
            ('/home/albert/projects/htmledit/viewhtml.py', 'viewhtml'),
            ('/home/albert/projects/mylinter/start.py', 'lintergui'),
            ('/home/albert/projects/compare-tool/actif.py', 'comparer'),
            ('/home/albert/projects/rst2html/rstviewer.py', 'rstview'),
            ('/home/albert/projects/csvtool/csvhelper.py', 'csvhelper'),
            ('/home/albert/projects/albumsgui/start.py', 'albums'),
            ('/home/albert/projects/mylinter/lint-this', 'lint-this'),
            ('/home/albert/projects/doctree/dt_print.py', 'dt_print'))
    for src, dst in data:
        os.symlink(src, dst)

ns = Collection()
ns.add_collection(session)
ns.add_collection(repo)
ns.add_collection(tags)
ns.add_collection(www)
ns.add_collection(lang)
ns.add_collection(db)
ns.add_task(listbin)
ns.add_task(install_scite)
ns.add_task(build_scite)
ns.add_task(arcstuff)
ns.add_task(chmodrecursive)
