from __future__ import print_function
import os
import shutil
import datetime
from fabric.api import *
from settings import *
## from pathlib import Path # toch maar niet gebruikt vanwege unicode errors bij write
import collections
import re
import glob
import csv
import functools
import logging
logging.basicConfig(filename="/home/albert/bin/log/fabfile_log", level=logging.DEBUG,
    format='%(asctime)s %(message)s')

"""collection of shortcut functions for common tasks like

. installing a new version of SciTE
. archiving a predefined set of files
. managing mongodb (start/stop/restart server and repair)
. managing posgresql (start/stop/restart server and repair)
. copying a file from the local to the webserver www directory
. helper functions for (py)gettext internationalization
"""

today = datetime.datetime.today()

def _log(message):
    logging.info(message)

#
# miscellaneous
#
def install_scite(version):
    """upgrade SciTE. argument: version number as used in filename
    """
    filename = os.path.abspath('Downloads/SciTE/gscite{}.tgz'.format(version))
    if not os.path.exists(filename):
        print('{} does not exist'.format(filename))
        return
    local('tar -zxf {}'.format(filename))
    local('sudo cp gscite/SciTE /usr/bin')
    local('sudo cp gscite/*.properties /etc/scite') # /usr/share/scite')
    local('sudo cp gscite/*.html /usr/share/scite')
    local('sudo cp gscite/*.png /usr/share/scite')
    local('sudo cp gscite/*.jpg /usr/share/scite')
    local('rm gscite -r')

def build_scite(version):
    """(re)build SciTE. argument: version number as used in filename

    standard binary is 32-bit and my system is 64-bit, so I need this now
    """
    filename = os.path.abspath('Downloads/SciTE/scite{}.tgz'.format(version))
    if not os.path.exists(filename):
        print('{} does not exist'.format(filename))
        return
    logfile = '/tmp/scite_build.log'
    with open(logfile, 'w') as _out:
        with settings(hide('running', 'warnings'), warn_only=True):
            with lcd('/tmp'):
                result = local('tar -zxf {}'.format(filename))
                # looks like he's not gzipping anymore, if so then try again
                if result.failed:
                    local('tar -xf {}'.format(filename))
            with lcd('/tmp/scintilla/gtk'):
                result = local('make', capture=True)
            _out.write(result.stdout + "\n")
            if result.failed:
                err = 'make scintilla failed'
            else:
                with lcd('/tmp/scite/gtk'):
                    err = ''
                    result = local('make', capture=True)
                    _out.write(result.stdout + "\n")
                    if result.failed:
                        err = 'make scite failed'
                    else:
                        result = local('sudo make install', capture=True)
                        _out.write(result.stdout + "\n")
                        if result.failed:
                            err = 'make install failed'
    if err:
        print('{}, see {}'.format(err, logfile))
    else:
        print('ready, see {}'.format(logfile))

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

#
# database server stuff
#
def start_mongo():
    "start mongo database server"
    local('sudo service mongodb start')

def stop_mongo():
    "stop mongo database server"
    local('sudo service mongodb stop')

def restart_mongo():
    "restart mongo database server"
    local('sudo service mongodb restart')

def repair_mongo():
    "repair mongo db"
    local('sudo rm /var/lib/mongodb/mongodb.lock')
    local('sudo mongod --dbpath /var/lib/mongodb/ --repair')
    local('sudo chmod 777 /var/lib/mongodb')

def start_pg():
    "start postgresql database server"
    local('sudo service postgresql start')

def stop_pg():
    "stop postgresql database server"
    local('sudo service postgresql stop')

def restart_pg():
    "restart postgresql database server"
    local('sudo service postgresql restart')

#
# default webserver stuff
#
def wwwcopy(*names):
    "copy indicated file(s) from ~/www/nginx-root to real nginx root"
    for name in names:
        local('sudo cp ~/www/nginx-root/{0} {1}/{0}'.format(name, server_root))

def wwwedit(*names):
    "edit indicated file(s) in ~/www/nginx-root"
    for name in names:
        local('scite ~/www/nginx-root/{0}'.format(name))

def wwwsites():
    "update mydomains database and localhost/sites.html from /etc/hosts"
    with lcd('~/www/django/mydomains'):
        local('python check_hosts.py')
    wwwcopy('sites.html')

def wwwedit_apache(name):
    "edit indicated file in apache root as-if edited directly"
    local('cp {1}/{0} /tmp/{0}'.format(name, apache_root))
    ## get('{1}/{0} /tmp'.format(name, apache_root))
    local('scite /tmp/{0}'.format(name))
    local('sudo cp /tmp/{0} {1}/{0}'.format(name, apache_root))
    ## put('/tmp/{0} {1}'.format(name, apache_root), use_sudo=True)

#
# language support stuff
#
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

#
# project/session management
#
def startproject(name):
    """start a new (Python) software project in a standardized way
    """
    loc = '/home/albert/projects/{}'.format(name)
    if os.path.exists(loc):
        print('sorry, this project name is already in use')
        return
    shutil.copytree('/home/albert/projects/skeleton', loc)
    os.rename(os.path.join(loc, 'projectname'), os.path.join(loc, name))
    tests_file = os.path.join(loc, 'tests', name + '_tests.py')
    os.rename(os.path.join(loc, 'tests', 'projectname_tests.py'), tests_file)
    with open(tests_file) as _in:
        data = _in.read()
    with open(tests_file, 'w') as _out:
        _out.write(data.replace('projectname', name))

def start_session(name):
    """start a programming session using various tools

    expects a session script of the same name in .sessions (subdirectory for now)
    each line contains a command to be executed
    """
    fname = os.path.expanduser('~/bin/.sessions/{}'.format(name))
    local('/bin/sh {}'.format(fname))

#
# routines for handling local and remote Mercurial repositories
#
def _check(context='local', push='no'):
    """vergelijkt mercurial repositories met elkaar

    context geeft aan welke: lokale working versie met lokale centrale versie,
    lokale centrale versie met bitbucket versie of usb versie met centrale versie
    push geeft aan of er ook gepushed moet worden (working naar centraal, centraal
    naar bitbucket of centraal naar usb) en moet indien van toepassing
    expliciet als 'yes' worden opgegeven (in het geval van usb wordt feitelijk
    gepulled, push vanuit usb moet altijd per repo apart)
    voor correcte werking m.b.t. pushen naar bitbucket moet voor elke repo een file
    <reponame>_tip aanwezig zijn met daarin de output van commando hg_tip
    """
    bb = context == 'bb'
    usb = context == 'usb'
    if context == 'local':
        root, outfile = '/home/albert', '/tmp/hg_local_changes'
    elif bb:
        root, outfile = '/home/albert/hg_repos', '/tmp/hg_changes'
    elif usb:
        root, outfile = '/media/albert/KINGSTON', '/tmp/hg_usb_changes'
    else:
        print('wrong context for this routine')
        return

    changes = False
    with open(outfile, 'w') as _out, settings(hide('running', 'warnings'),
            warn_only=True):
        print('check {} repos on {}\n\n'.format(context, today), file=_out)
        for name in all_repos:
            stats = []
            if bb and name in non_bb_repos:
                continue
            if bb and name in private_repos:
                pwd = os.path.join(root.replace('repos', 'private'), name)
            elif name == 'bitbucket':
                if bb:
                    pwd = os.path.join(root, 'avisser.bitbucket.org')
                else:
                    pwd = os.path.join(root, 'www', name)
            elif name in django_repos and not bb:
                proj = name.split('-')[0] if name.startswith('magiokis') else name
                pwd = os.path.join(root, 'www', 'django', proj)
            elif name in cherrypy_repos and not bb:
                proj = name.split('-')[0] if name.startswith('magiokis') else name
                pwd = os.path.join(root, 'www', 'cherrypy', proj)
            elif name not in private_repos and not bb and not usb:
                proj = name.replace('-', '_') if name.startswith('magiokis') else name
                pwd = os.path.join(root, 'projects', proj)
            else:
                pwd = os.path.join(root, name)

            tmp = '/tmp/hg_st_{}'.format(name)
            uncommitted = outgoing = incoming = False
            with lcd(pwd):
                result = local('hg status --quiet', capture=True)
            test = result.stdout
            if test.strip():
                stats.append('uncommitted changes')
                print('\nuncommitted changes in {}'.format(pwd), file=_out)
                uncommitted = True
                _out.write(test + '\n')
            if bb:
                tmpfile = os.path.join('/tmp', '{}_tip'.format(name))
                tipfile = os.path.join(root, '{}_tip'.format(name))
                with lcd(pwd):
                    local('hg tip > {}'.format(tmpfile))
                with open(tmpfile) as _in1, open(tipfile) as _in2:
                    buf1 = _in1.read()
                    buf2 = _in2.read()
                outgoing = buf1 != buf2
                if outgoing:
                    stats.append('outgoing changes')
                    print('outgoing changes for {}'.format(name), file=_out)
                    _out.write("--local:\n")
                    _out.write(buf1 + "\n")
                    _out.write("-- bb:\n")
                    _out.write(buf2 + "\n")
            else:
                with lcd(pwd):
                    result = local('hg outgoing', capture=True)
                outgoing = result.succeeded
                if outgoing:
                    changes = True
                    stats.append('outgoing changes')
                    print('\noutgoing changes for {}'.format(name), file=_out)
                    _out.write(result.stdout + '\n')
                if usb:
                    with lcd(pwd):
                        result = local('hg incoming', capture=True)
                    incoming = result.succeeded
                    if incoming:
                        changes = True
                        stats.append('incoming changes')
                        print('\nincoming changes for {}'.format(name), file=_out)
                        _out.write(result.stdout + '\n')
            if stats:
                print(' and '.join(stats) + ' for {}'.format(name))
            else:
                print('no changes for {}'.format(name))
            if uncommitted or outgoing or incoming: changes = True
            if push != 'yes':
                continue
            command = ''
            if not usb:
                if outgoing:
                    command = 'hg push' # if bb else 'hg push --remotecmd "hg update"'
                    # remotecmd werkt niet zo maar geen idee hoe dan wel
            else:
                if incoming: #  and not uncommitted and not outgoing:
                    command = 'hg pull --update'
            if command:
                with lcd(pwd):
                    result = local(command)
                    if result.succeeded:
                        _out.write(result.stdout + '\n')
                        if bb:
                            with lcd(pwd):
                                local('hg tip > {}'.format(tipfile))
    print()
    if changes:
        print('for details see {}'.format(outfile))
    else:
        print('no change details')

def check_local():
    """compare hg repositories: working vs "central"
    """
    _check()

def check_bb():
    """compare hg repositories: "central" vs BitBucket
    """
    _check('bb')

def check_usb():
    """compare hg repositories: "central" vs usb stick
    """
    _check('usb')

def push_local():
    """push from working to "central"
    """
    _check(push='yes')

def push_bb():
    """push from "central" to BitBucket
    """
    _check('bb', push='yes')

def push_usb():
    """push from "central" to usb stick (implemented as a pull)
    """
    _check('usb', push='yes')

def pull_usb():
    """not implemented yet: push from usb to "central"
    """

def pull_local():
    """not implemented yet: push from "central" to working
    """

def pushthru(*names):
    """push from working to "central" and on to bitbucket if possible

    either name specific repos or check all
    when no name is specified, the "_check" variants are used
    """
    all_repos = bb_repos + private_repos
    if not names:
        ## names = all_repos
        _check(push='yes')
        _check('bb', push='yes')
        with open('/tmp/pushthru_log', 'w') as _out:
            for fname in ('/tmp/hg_local_changes', '/tmp/hg_changes'):
                with open(fname) as _in:
                    for line in _in:
                        _out.write(line)
        print('\nready, output in /tmp/pushthru_log')
        return
    with open('/tmp/pushthru_log', 'w') as _out:
        for name in names:
            if name not in all_repos:
                logline = '{} not pushed: is not on bitbucket'.format(name)
                print(logline)
                _out.write(logline + "\n")
                continue
            localpath = os.path.join('~', 'projects', name)
            centralpath = os.path.join('~', 'hg_repos', name)
            if name in private_repos:
                localpath = os.path.join('~', name)
                centralpath = centralpath.replace('repos', 'private')
            elif name in django_repos:
                localpath = localpath.replace('projects', os.path.join('www',
                    'django'))
            elif name in cherrypy_repos:
                localpath = localpath.replace('projects', os.path.join('www',
                    'cherrypy'))
            elif name ==  'bitbucket':
                localpath = localpath.replace('projects', 'www')
                centralpath = centralpath.replace(name, 'avisser.bitbucket.org')
            with settings(hide('running', 'warnings'), warn_only=True):
                with lcd(localpath):
                    result = local('hg outgoing', capture=True)
                _out.write(result.stdout + "\n")
                if result.failed:
                    logline = '{} - hg outgoing failed'.format(name)
                    _out.write(logline + "\n")
                    _out.write(result.stderr + "\n")
                else:
                    with lcd(localpath):
                        result = local('hg push --remotecmd update', capture=True)
                    _out.write(result.stdout + "\n")
                    if result.failed:
                        logline = '{} - pushing failed'.format(name)
                        _out.write(logline + "\n")
                        _out.write(result.stderr + "\n")
                        continue
                with lcd(centralpath):
                    result = local('hg push', capture=True)
                _out.write(result.stdout + "\n")
                if result.failed:
                    logline = '{} - pushing to bitbucket failed'.format(name)
                    _out.write(logline + "\n")
                    _out.write(result.stderr + "\n")
    print('ready, output in /tmp/pushthru_log')

def _make_repolist(path):
    """turn the repo log into a history

    input: pathname to the repository
    output: dictionary containing the history
    """
    ## logging.info('processing {}'.format(item))
    with settings(hide('running', 'warnings'), warn_only=True):
        with lcd(path):
            result = local('hg log -v', capture=True)
            data = result.stdout
    outdict = collections.defaultdict(dict)
    in_description = False
    for line in data.split('\n'):
        line = line.strip()
        words = line.split()
        if line == '':
            in_description = False
        elif in_description:
            outdict[key]['desc'].append(line)
        elif words[0] == 'changeset:':
            key, _ = words[1].split(':', 1)
            key = int(key)
        elif words[0] == 'date:':
            outdict[key]['date'] = ' '.join(words[1:])
        elif words[0] == 'files:':
            outdict[key]['files'] = words[1:]
        elif words[0] == 'description:':
            in_description = True
            outdict[key]['desc'] = []
    return outdict

def _make_repo_ovz(outdict, outfile):
    """write the history to a file

    input: history in the form of a dictionary, output filename
    output: the specified file as written to disk
    """
    with open(outfile, "w") as _out:
        for key in sorted(outdict.keys()):
            _out.write('{}: {}\n'.format(outdict[key]['date'],
                '\n'.join(outdict[key]['desc'])))
            try:
                for item in outdict[key]['files']:
                    _out.write('    {}\n'.format(item))
            except KeyError:
                pass

def _make_repocsv(outdict, outfile):
    """turn the repo history into a comma delimited file

    input: history in the form of a dictionary, output filename
    output: the specified file as written to disk
    """
    def listnn(count):
        return count * [""]
    date_headers, desc_headers = [" \\ date"], ["filename \\ description"]
    in_changeset_dict = collections.defaultdict(functools.partial(listnn, len(outdict.keys())))
    for key in sorted(outdict.keys()):
        date_headers.append(outdict[key]['date'])
        desc = "\n".join(outdict[key]['desc'])
        if ',' in desc or ';' in desc:
            desc = '"{}"'.format(desc)
        desc_headers.append(desc)
        try:
            filelist = outdict[key]['files']
        except KeyError:
            continue
        for item in filelist:
            if '/' not in item: item = './' + item
            in_changeset_dict[item][int(key)] = "x"
    with open(outfile, "wb") as _out:
        writer = csv.writer(_out)
        writer.writerow(date_headers)
        writer.writerow(desc_headers)
        for key in sorted(in_changeset_dict):
            out = [key] + in_changeset_dict[key]
            writer.writerow(out)

def _repos_overzicht(name, path):
    if not os.path.isdir(path): return
    if '.hg' not in os.listdir(path): return
    print('processing repository: {}'.format(name))
    outdict = _make_repolist(path)
    ## outfile = os.path.join(root, ".overzicht", "{}.repo_ovz".format(name))
    ## _make_repo_ovz(outdict, outfile)
    outfile = os.path.join(os.path.dirname(path), ".overzicht", "{}.csv".format(name))
    _make_repocsv(outdict, outfile)

def repos_overzicht(*names):
    """Try to build a history file
    from a repository log - meant to help me decide on tags or versions
    """
    root = '/home/albert/hg_repos'
    if not names:
        names = [x for x in os.listdir(root)]
    for item in names:
        path = os.path.join(root, item)
        _repos_overzicht(item, path)
#
# routines for repos that are not kept intact when deployed (e.g. plain cgi websites)
#
def _get_mapping(proj):
    project_path = os.path.join(projects_base, proj)
    mapping_file = os.path.join(project_path, 'paths.conf')
    # read directory mapping
    path_map = []
    with open(mapping_file) as _in:
        for line in _in:
            try:
                in_repo, in_deploy = line.strip().split('=')
            except ValueError as e:
                continue
            path_map.append((in_repo, os.path.join(project_path, in_repo),
                os.path.expanduser(in_deploy)))
    return path_map

def _get_files(proj):
    project_path = os.path.join(projects_base, proj)
    tracked, ignored = [], []
    with lcd(project_path), settings(hide('running', 'warnings'), warn_only=True):
        result = local('hg manifest', capture=True)
        tracked = result.stdout.split('\n')
    with open(os.path.join(project_path, '.hgignore')) as _in:
        subincludes = []
        syntax = 'regexp'
        for line in _in:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('syntax:'):
                syntax = line.replace('syntax:', '').strip()
                continue
            if line.startswith('subinclude:'):
                subincludes.append(line)
            ignored.append((line, syntax))
        # TODO: process subincludes
        return tracked, ignored

def _get_next(last, gen):
    ended = False
    try:
        last = next(gen)
    except StopIteration:
        ended = True
    return ended, last

def _check_ignored(name, tracked, ignored, path):
    if name in tracked:
        return False
    sep = '/'
    for pattern, syntax in ignored:
        if sep in pattern:
            subdir, pattern = pattern.split(sep, 1)
            test = os.path.basename(path)
            if subdir != test:
                continue # zinloos om verder te kijken
        all_files = glob.glob(os.path.join(path, pattern))
        if syntax == 'regexp' and re.match(pattern, name):
            return True
        elif syntax == 'glob' and os.path.join(path, name) in all_files:
            return True
    return False

def _check_project(proj):
    project_path = os.path.join(projects_base, proj)
    # make inventory
    tracked, ignored = _get_files(project_path)
    inserts, deletes, changed = [], [], []
    difflist, results = [], []
    for subdir, repo_path, deploy_path in _get_mapping(proj):
        # ignoring subdirectories for now
        repofiles = (x for x in sorted(os.listdir(repo_path))
            if os.path.isfile(os.path.join(repo_path, x)))
        deployfiles = (x for x in sorted(os.listdir(deploy_path))
            if os.path.isfile(os.path.join(deploy_path, x)))
        keeps = []
        ended1, old = _get_next('', repofiles)
        ended2, new = _get_next('', deployfiles)
        while not ended1 and not ended2:
            if old > new:
                if not _check_ignored(new, tracked, ignored, deploy_path):
                    inserts.append(os.path.join(subdir, new))
                ended2, new = _get_next(new, deployfiles)
            else:
                if _check_ignored(old, tracked, ignored, repo_path):
                    continue
                if old < new:
                    if not _check_ignored(old, tracked, ignored, repo_path):
                        deletes.append(os.path.join(subdir, old))
                    ended1, old = _get_next(old, repofiles)
                else:
                    if not _check_ignored(old, tracked, ignored, repo_path):
                        keeps.append((old, new))
                    ended1, old = _get_next(old, repofiles)
                    ended2, new = _get_next(new, deployfiles)
        # we have our inserts and deletes, now check for changes
        for old, new in keeps:
            oldname = os.path.join(repo_path, old)
            newname = os.path.join(deploy_path, new)
            with settings(hide('running', 'warnings'), warn_only=True):
                result = local('diff {} {}'.format(oldname, newname), capture=True)
                if result.failed:
                    changed.append(os.path.join(subdir, old))
                    difflist.append('< ' + oldname)
                    difflist.append('> ' + newname)
                    difflist.append(result.stdout)
                    difflist.append(result.stderr)
    if deletes:
        results.append('files in repo, not in deploy - possible removals')
        for name in deletes:
            results.append('    {}'.format(name))
    if inserts:
        results.append('files in deploy, not in repo - possible additions')
        for name in inserts:
            results.append('    {}'.format(name))
    if changed:
        results.append('common files that are different - probable changes')
        for name in changed:
            results.append('    {}'.format(name))
    return results, difflist

not_suitable = 'project name {} not suitable for repocheck/repocopy'
def repocheck(*names):
    """check for modifications in repositories that are spread over various deploy
    locations (mainly plain cgi web applications)
    """
    if not names:
        names = non_deploy_repos
    results, output = [], []
    for name in names:
        if name not in non_deploy_repos:
            print(not_suitable.format(name))
            continue
        filelist, difflist = _check_project(name)
        if filelist:
            output.append('possible changes for {}'.format(name))
            for item in filelist:
                output.append(item)
            results.append('=== project: {} ==='.format(name))
            results.extend(filelist)
            results.extend(difflist)
        else:
            output.append('no changes for {}'.format(name))
    with open('/tmp/reposync_status', 'w') as _out:
        for line in results:
            print(line, file=_out)
    for item in output:
        print(item)
    if results:
        print('see /tmp/reposync_status for details')

def _repocopy(repo, path, name):
    found = False
    for subdir, repopath, deploypath in _get_mapping(repo):
        if subdir == path:
            found = True
            break
    if not found:
        print('repository {} subpath {} not found'.format(repo, path))
        return
    try:
        shutil.copyfile(os.path.join(deploypath, name), os.path.join(repopath, name))
        print('copy {} from {} to {}'.format(name, deploypath, repopath))
    except IOError:
        print('file {} not found in deploy path for {}/{}'.format(os.path.join(path,
            name), repo, path))

def repocopy(repo=None, file=None):
    """copy a file from the remote (deploy) location into the (working) repo

    no parameters: copy all changes
    one parameter: if only repo specified: copy all changes for this repo
    two parameters: if both repo and file specified: copy specific file
    otherwise: error
    """
    usage = "abort: usage is fab repocopy:repo=<reponame>,file=<pathname>/<filename>"
    repos, files = [], []
    if repo:
        repos = [repo]
    else:
        repos = non_deploy_repos
    if file:
        if len(repos) == 1:
            try:
                subdir, name = file.rsplit(os.sep, 1)
            except ValueError:
                print(usage)
            else:
                _repocopy(repo, subdir, name)
        else:
            print(usage)
        return
    for projname in repos:
        if projname not in non_deploy_repos:
            print(not_suitable.format(projname))
            continue
        filelist, difflist = _check_project(projname)
        for file in filelist:
            try:
                subdir, filename = file.strip().rsplit(os.sep, 1)
            except ValueError:
                continue
            _repocopy(projname, subdir, filename)
