"""import Invoke commands from various location as well as define some others
"""
import os
import os.path
import stat
import datetime
import contextlib
from invoke import task, Collection

# import settings
import session
import repo
import tags
import www
import lang
import db
import scriptlib
HERE = os.path.expanduser('~/bin')
SCITELOC = os.path.expanduser('~/Downloads/SciTE/scite{}.tgz')
GSCITELOC = os.path.expanduser('~/Downloads/SciTE/gscite{}.tgz')


@task(help={'version': 'Version of sciTE to install'})
def install_scite(c, version):
    """upgrade SciTE. argument: version number as used in filename
    """
    filename = GSCITELOC.format(version)
    if not os.path.exists(filename):
        print(f'{filename} does not exist')
        return
    # with settings(hide('running', 'warnings'), warn_only=True):
    result = c.run(f'tar -zxf {filename}')
    if result.failed:
        result = c.run(f'tar -xf {filename}')
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
    filename = SCITELOC.format(version)
    if not os.path.exists(filename):
        print(f'{filename} does not exist')
        return
    logfile = '/tmp/scite_build.log'
    with open(logfile, 'w') as _out:
        with c.cd('/tmp'):
            result = c.run(f'tar -zxf {filename}')
            # looks like he's not gzipping anymore, if so then try again
            if result.failed:
                c.run(f'tar -xf {filename}')
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
    if not err:
        err = 'ready'
    print(f'{err}, see {logfile}')


@task(help={'names': 'list of files containing the files to backup'})
def arcstuff(c, names):
    """backup selected files indicated in a .conf file

    use the value 'all' to select all arcstuff config files present
    """
    if names == 'all':
        files = [x for x in os.listdir(HERE)
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
            fname = f'arcstuff{hlp}.conf'
            if not os.path.exists(fname):
                raise ValueError(f'abort: no config file for {name} ({fname} does not exist)')
            files.append(fname)
    for indx, infile in enumerate(files):
        name = 'all' if not names[indx] else names[indx]
        dts = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
        outfile = os.path.expanduser(f'~/arcstuff/{name}_{dts}.tar.gz')
        with open(infile) as f_in:
            ## first = True
            command = f'tar -czvf {outfile}'
            prepend = ''
            for line in f_in:
                line = line.strip()
                if line.startswith('['):
                    if line.endswith(']'):
                        prepend = line[1:-1]
                    continue
                if not line or line.startswith('#'):
                    continue
                with contextlib.suppress(ValueError):
                    line, rest = line.split('#', 1)
                path = os.path.join(prepend, line) if prepend else line
                command = f'{command} {path.strip()}'
        c.run(command)


ns = Collection()
ns.add_collection(session)
ns.add_collection(repo)
ns.add_collection(tags)
ns.add_collection(www)
ns.add_collection(lang)
ns.add_collection(db)
ns.add_collection(scriptlib)
ns.add_task(install_scite)
ns.add_task(build_scite)
ns.add_task(arcstuff)
