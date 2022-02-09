"""Invoke routines for handling local and remote Mercurial and Git repositories
"""
import os
import os.path
import collections
import functools
import datetime
import csv
from invoke import task
from settings import (get_project_dir, all_repos, git_repos, private_repos, django_repos,
                      cherrypy_repos, frozen_repos)

HOME = os.path.expanduser('~')
TODAY = datetime.datetime.today()
FILELIST = '/tmp/~~pfind'


def get_repofiles(c, reponame):
    """get all files from manifest
    """
    path = ''
    if reponame == '.':
        path = os.getcwd()
        reponame = os.path.basename(path)
    else:
        path = get_project_dir(reponame)
    if not path:
        print('not a code repository')
        return '', []
    use_git = True   # if reponame in git_repos else False
    with c.cd(path):
        command = 'git ls-tree -r --name-only master' if use_git else 'hg manifest'
        result = c.run(command, hide=True)
    files = [x for x in result.stdout.split('\n') if os.path.splitext(x)[1] == '.py']
    return path, files


def get_branchname(c, pwd):
    with c.cd(pwd):
        result = c.run('git branch', hide=True)
    name = ''
    for line in result.stdout.split('\n'):
        if line.startswith('*'):
            name = line.split()[1]
            break
    if name == 'master':
        return ''
    return name


def _check(c, context='local', push='no', verbose=False, exclude=None, dry_run=False):
    """vergelijkt repositories met elkaar

    context geeft aan welke:
    'local':  lokale working versie met lokale centrale versie,
    'remote': lokale centrale versie met bitbucket of github versie
    'verbose': geef ook 'no changes' meldingen
    'exclude' maakt het mogelijk om repos uit te sluiten van verwerking
    push geeft aan of er ook gepushed moet worden (working naar centraal, centraal
    naar bitbucket of github) en moet indien van toepassing
    expliciet als 'yes' worden opgegeven
    voor correcte werking m.b.t. pushen naar remote moet voor elke repo een file
    <reponame>_tip aanwezig zijn met daarin de output van commando hg tip of
    in het geval van git log -r -1
    """
    if exclude is None:
        # exclude = []
        exclude = frozen_repos
    local_ = context == 'local'
    remote = not local_
    if context not in ('local', 'remote'):
        print('wrong context for this routine')
        return ''
    elif local_:
        root, outfile = HOME, '/tmp/repo_local_changes'
    else:
        root, outfile = os.path.join(HOME, 'hg_repos'), '/tmp/repo_changes'

    changes = False
    with open(outfile, 'w') as _out:
        _out.write('check {} repos on {}\n\n'.format(context, TODAY))
        for name in all_repos:
            if name in exclude:
                continue
            is_gitrepo = name in git_repos
            is_private = name in private_repos
            stats = []
            pwd = os.path.join(root, name)
            if remote:
                if is_gitrepo or is_private:
                    pwd = os.path.join(root.replace('hg', 'git'), name)
                    root = root.replace('hg', 'git')
            elif local_:
                if is_private:
                    pwd = os.path.join(root, private_repos[name])
                else:
                    pwd = os.path.join(root, 'projects', name)

            uncommitted = outgoing = False
            # check if we are on branch 'master'
            not_on_master = get_branchname(c, pwd) if is_gitrepo or is_private else ''

            command = 'git status -uno --short' if (is_gitrepo or is_private) else 'hg status --quiet'
            if dry_run:
                print('execute `{}` in directory `{}`'.format(command, pwd))
                test = ''
            else:
                with c.cd(pwd):
                    result = c.run(command, hide=True)
                test = result.stdout
            if test.strip():
                on_branch = ' (on branch {})'.format(not_on_master) if not_on_master else ''
                stats.append('uncommitted changes' + on_branch)
                _out.write('\nuncommitted changes in {}{}\n'.format(pwd, on_branch))
                uncommitted = True
                _out.write(test + '\n')
            outgoing = use_tipfile = False
            result = None
            if is_gitrepo or is_private:
                command = 'git log origin/master..master'
            elif remote:
                tmpfile = os.path.join('/tmp', '{}_tip'.format(name))
                tipfile = os.path.join(root, '{}_tip'.format(name))
                if not os.path.exists(tipfile):
                    command = 'touch {}'.format(tipfile)
                    if dry_run:
                        print('execute `{}`'.format(command))
                    else:
                        c.run(command)
                command = 'hg tip'
                use_tipfile = True
            else:
                command = 'hg outgoing'
            if dry_run:
                print('execute `{}` in directory `{}`'.format(command, pwd))
            else:
                if use_tipfile:
                    with c.cd(pwd):
                        c.run('{} > {}'.format(command, tmpfile))
                    with open(tmpfile) as _in1, open(tipfile) as _in2:
                        buf1 = _in1.read()
                        buf2 = _in2.read()
                    outgoing = buf1 != buf2
                else:
                    with c.cd(pwd):
                        result = c.run(command, warn=True, hide=True)
                        # print(result, result.ok, result.stdout, result.stderr)
                        if is_gitrepo or is_private:
                            outgoing = result.stdout.strip()
                        else:
                            outgoing = result.ok
            if outgoing:
                stats.append('outgoing changes')
                _out.write('outgoing changes for {}\n'.format(name))
                if use_tipfile:
                    _out.write("--local:\n")
                    _out.write(buf1 + "\n")
                    _out.write("-- remote:\n")
                    _out.write(buf2 + "\n")
                elif result:
                    _out.write(result.stdout + '\n')
            if stats:
                print(' and '.join(stats) + ' for {}'.format(name))
            elif verbose:
                print('no changes for {}'.format(name))
            if uncommitted or outgoing:
                changes = True
            if push != 'yes':
                continue
            if not outgoing:
                continue
            if is_gitrepo or is_private:
                ref = '-u' if remote else ''
                command = 'git push {} origin master'.format(ref)
            else:
                command = 'hg push'  # if bb else 'hg push --remotecmd "hg update"'
                # remotecmd werkt niet zo maar geen idee hoe dan wel
            if dry_run:
                print('execute `{}` in directory `{}`'.format(command, pwd))
                # simulate result.ok somehow?
            else:
                with c.cd(pwd):
                    result = c.run(command)
            if result.ok:
                _out.write(result.stdout + '\n')
                if remote and use_tipfile:
                    command = 'git log -r -1' if is_gitrepo or is_private else 'hg tip'
                    if dry_run:
                        print('execute `{}` in directory `{}`'.format(command, pwd))
                    else:
                        with c.cd(pwd):
                            c.run('{} > {}'.format(command, tipfile))
                else:
                    if not is_gitrepo and not is_private:
                        command = 'hg up'
                        if dry_run:
                            print('execute `{}` in directory `{}`'.format(command, pwd))
                        else:
                            with c.cd(pwd):
                                result = c.run(command)
                                _out.write(result.stdout + '\n')

    print()
    if changes:
        print('for details see {}'.format(outfile))
    else:
        print('no change details')
    return changes


@task
def check_local(c, dry_run=False):
    """compare all local repositories: working vs "central"
    """
    test = _check(c, dry_run=dry_run)
    if test:
        print("use 'check-repo <reponame>' to inspect changes")
        print("    'binfab repo.check-local-notes` for remarks")


@task
def check_local_changes(c):
    "view output of check_local command"
    with c.cd('~/projects'):
        c.run('gnome-terminal --geometry=100x40 -- view /tmp/repo_local_changes')


@task
def check_local_notes(c):
    "view remarks on repofiles not to be committed / pushed yet"
    with c.cd('~/projects'):
        # c.run("a-propos -n 'Ongoing stuff not needing to be committed yet' -f ongoing.apo &")
        c.run('treedocs projects.trd')


@task
def check_remote(c, dry_run=False):
    """compare all hg repositories: "central" vs BitBucket / GitHub
    """
    _check(c, 'remote', dry_run=dry_run)


@task(help={'exclude': 'comma separated list of repostories not to push'})
def push_local(c, exclude=None, dry_run=False):
    """push all repos from working to "central" with possibility to exclude
    To exclude multiple repos you need to provide a string with escaped commas
    e.g. binfab push_remote
         binfab push remote:exclude=apropos
         binfab push_remote:exclude="apropos,albums"
    """
    _check(c, push='yes', exclude=exclude, dry_run=dry_run)


@task(help={'exclude': 'comma separated list of repostories not to push'})
def push_remote(c, exclude=None, dry_run=False):
    """push all repos from "central" to BitBucket with possibility to exclude
    To exclude multiple repos you need to provide a string with escaped commas
    e.g. binfab push_remote
         binfab push remote:exclude=apropos
         binfab push_remote:exclude="apropos,albums"
    """
    _check(c, 'remote', push='yes', exclude=exclude, dry_run=dry_run)


@task(help={'names': 'comma separated list of repostories to push'})
def pushthru(c, names):
    """push from working to "central" and on to bitbucket if possible

    either name specific repos or check all
    when no name is specified, the "_check" variants are used
    """
    if not names:
        _check(c, push='yes')
        _check(c, 'remote', push='yes')
        with open('/tmp/pushthru_log', 'w') as _out:
            for fname in ('/tmp/repo_local_changes', '/tmp/repo_changes'):
                with open(fname) as _in:
                    for line in _in:
                        _out.write(line)
        print('\nready, output in /tmp/pushthru_log')
        return
    print('niet uitgevoerd, moet herschreven worden o.a. naar gebruik van git')
    return
    errors = False
    with open('/tmp/pushthru_log', 'w') as _out:
        for name in names.split(','):
            if name not in all_repos:
                # logline = '{} not pushed: is not on bitbucket'.format(name)
                logline = '{} not pushed: is not registered as a remote repo'.format(name)
                print(logline)
                _out.write(logline + "\n")
                errors = True
                continue
            localpath = os.path.join('~', 'projects', name)
            # centralpath = os.path.join('~', 'hg_repos', name)
            centralpath = os.path.join('~', 'git_repos', name)
            # TODO nog rekening houden met repos in .frozen?
            if name in private_repos:
                localpath = os.path.join('~', name)
                centralpath = centralpath.replace('repos', 'private')
            # elif name in django_repos:  # ??
            #     localpath = localpath.replace('projects', os.path.join('www', 'django'))
            # elif name in cherrypy_repos:  # ??
            #     localpath = localpath.replace('projects', os.path.join('www', 'cherrypy'))
            # elif name == 'bitbucket':
            #     localpath = localpath.replace('projects', 'www')
            #     centralpath = centralpath.replace(name, 'avisser.bitbucket.org')
            with c.cd(localpath):
                # TODO dit moet nog met git log zoals in _check
                # result = c.run('hg outgoing', warn=True, hide=True)
                result = c.run('git log origin/master..master', warn=True, hide=True)
            _out.write(result.stdout + "\n")
            if result.failed:
                # logline = '{} - hg outgoing failed'.format(name)
                logline = '{} - git outgoing check failed'.format(name)
                _out.write(logline + "\n")
                _out.write(result.stderr + "\n")
                errors = True
            else:
                with c.cd(localpath):
                    # result = c.run('hg push --remotecmd update', warn=True, hide=True)
                    result = c.run('git push', warn=True, hide=True)
                _out.write(result.stdout + "\n")
                if result.failed:
                    logline = '{} - pushing failed'.format(name)
                    _out.write(logline + "\n")
                    _out.write(result.stderr + "\n")
                    errors = True
                    continue
            with c.cd(centralpath):
                # result = c.run('hg push', warn=True, hide=True)
                result = c.run('git push', warn=True, hide=True)
            _out.write(result.stdout + "\n")
            if result.failed:
                # logline = '{} - pushing to bitbucket failed'.format(name)
                logline = '{} - pushing to github failed'.format(name)
                _out.write(logline + "\n")
                _out.write(result.stderr + "\n")
                errors = True
    extra = ' with errors' if errors else ''
    print('ready{}, output in /tmp/pushthru_log'.format(extra))


@task(help={'names': 'comma separated list of repostories to list',
            'outtype': 'format for output list - `csv` (default) or `txt`'})
def overview(c, names=None, outtype=''):
    """Try to build a history file from one or more repository logs
    meant to help me decide on tags or versions
    """
    print('uitgevoerd voor oude hg repo, moet herschreven worden o.a. naar gebruik van git')
    # print('niet uitgevoerd, moet herschreven worden o.a. naar gebruik van git')
    # return
    outtype = outtype or 'csv'
    if outtype not in ('txt', 'csv'):
        print('wrong spec for output type')
    root = '/home/albert/hg_repos'
    # root = '/home/albert/git_repos'
    # root = '/home/albert/projects'
    if not names:
        names = [x for x in os.listdir(root)]
    else:
        names = names.split(',')
    for item in names:
        path = os.path.join(root, item)
        outdir = repo_overzicht(c, item, path, outtype)
    print('output in {}'.format(outdir))  # os.path.join(os.path.dirname(path), ".overzicht")))


def repo_overzicht(c, name, path, outtype):
    """Try to build a history file from a repository log
    currently it shows which commits contain which files
    """
    repotype = ''
    if not os.path.isdir(path):
        return
    if '.hg' in os.listdir(path):
        outdict = make_repolist_hg(c, path)
        repotype = 'hg'
    elif '.hg' in os.listdir(path):
        outdict = make_repolist_git(c, path)
        repotype = 'git'
    else:
        return
    outdir = os.path.join(os.path.dirname(path), ".overzicht")
    if outtype == 'txt':
        outfile = os.path.join(outdir, "{}_repo.ovz".format(name))
        make_repo_ovz(outdict, outfile)
    elif outtype == 'csv':
        outfile = os.path.join(outdir, "{}_repo.csv".format(name))
        make_repocsv(outdict, outfile)
    return outdir


def make_repolist_hg(c, path):
    """turn the repo log into a history - mercurial version

    input: pathname to the repository
    output: dictionary containing the history
    """
    ## logging.info('processing {}'.format(item))
    with c.cd(path):
        result = c.run('hg log -v', hide=True)
        data = result.stdout
    outdict = collections.defaultdict(dict)
    in_description = False
    key = ''  # just to satisfy the linters
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
            outdict[key]['date'] = ' '.join(words[1:4] + [words[5], words[4], words[6]])
        elif words[0] == 'files:':
            outdict[key]['files'] = words[1:]
        elif words[0] == 'description:':
            in_description = True
            outdict[key]['desc'] = []
    return outdict


def make_repolist_git(c, path):
    """turn the repo log into a history - git version

    input: pathname to the repository
    output: dictionary containing the history
    """


def make_repo_ovz(outdict, outfile):
    """write the history to a file

    input: history in the form of a dictionary, output filename
    output: the specified file as written to disk
    """
    with open(outfile, "w") as _out:
        for key in sorted(outdict.keys()):
            _out.write('{}: {}\n'.format(outdict[key]['date'], '\n'.join(outdict[key]['desc'])))
            try:
                for item in outdict[key]['files']:
                    _out.write('    {}\n'.format(item))
            except KeyError:
                pass


def make_repocsv(outdict, outfile):
    """turn the repo history into a comma delimited file

    input: history in the form of a dictionary, output filename
    output: the specified file as written to disk
    """
    def listnn(count):
        "build list of empty strings"
        return count * [""]
    date_headers, desc_headers = [" \\ date"], ["filename \\ description"]
    in_changeset_dict = collections.defaultdict(
        functools.partial(listnn, len(outdict.keys())))
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
            if '/' not in item:
                item = './' + item
            in_changeset_dict[item][int(key)] = "x"
    with open(outfile, "w") as _out:
        writer = csv.writer(_out)
        writer.writerow(date_headers)
        writer.writerow(desc_headers)
        for key in sorted(in_changeset_dict):
            out = [key] + in_changeset_dict[key]
            writer.writerow(out)


@task(help={'name': 'repository name'})
def add2gitweb(c, name):
    "make a repository visible with gitweb"
    c.run('sudo ln -s ~/git_repos/{0}/.git /var/lib/git/{0}.git'.format(name))


def check_and_run_for_project(c, name, command):
    "run only if called for a valid project"
    if name:
        where = get_project_dir(name)
        if where:
            with c.cd(where):
                c.run(command)
        else:
            print('{} is not a known project'.format(name))
    else:
        where = os.getcwd()
        name = os.path.basename(where)
        if get_project_dir(name) == where:
            with c.cd(where):
                c.run(command)
        else:
            print('you are not in a known project directory')


@task
def dtree(c, name=''):
    "Open project docs using treedocs, forcing qt mode"
    check_and_run_for_project(c, name, '~/projects/doctree/ensure-qt projdocs.trd')


@task
def qgit(c, name=''):
    "Open Git gui after changing to repository"
    check_and_run_for_project(c, name, 'qgit')


@task
def mee_bezig(c, name=''):
    "Open Doing list for a project using a-propos"
    # check_and_run_for_project(c, name, "a-propos -n 'Mee Bezig ({})' -f mee_bezig.apo".format(
    #     name or os.path.basename(os.getcwd())))
    c.run('treedocs ~/projects/projects.trd')


@task
def preadme(c, name=''):
    "Open readme for project"
    check_and_run_for_project(c, name, 'pedit readme.rst')


@task
def prshell(c, name=''):
    "Open terminal for project with geometry and profile"
    check_and_run_for_project(c, name, 'gnome-terminal --geometry=132x43+4+40')


def rebuild_filenamelist(c):
    "build a list of all tracked Python files in all projects"
    all_files = []
    for repo in all_repos:
        if repo in frozen_repos:
            continue
        path, files = get_repofiles(c, repo)
        all_files.extend([os.path.join(path, x) for x in files])
    with open(FILELIST, 'w') as out:
        for line in sorted(all_files):
            print(line, file=out)


@task
def search(c, find='', rebuild=False):
    "search in all tracked python files in all repos"
    if not os.path.exists(FILELIST) or rebuild:
        rebuild_filenamelist(c)
    command = 'afrift -m multi {} -e py -P'.format(FILELIST)
    if find:
        command += 'N -s ' + find
    c.run(command)

