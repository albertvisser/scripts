"""Invoke routines for handling local and remote Mercurial and Git repositories
"""
import os
import os.path
import collections
import functools
import datetime
import csv
from invoke import task
from settings import (get_project_dir, get_project_root, all_repos, git_repos, private_repos,
                      django_repos, cherrypy_repos, frozen_repos)

HOME = os.path.expanduser('~')
TODAY = datetime.datetime.today()
FILELIST = '/tmp/~~pfind'
P2ULOG = '/tmp/pushthru_log'
REPOCHG = '/tmp/repo_changes'
LOCALCHG = '/tmp/repo_local_changes'


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


class Check:
    """vergelijkt repositories met elkaar

    `context` geeft aan welke:
    - 'local':  lokale working versie met lokale centrale versie,
    - 'remote': lokale centrale versie met bitbucket of github versie
    `verbose`: True geef ook 'no changes' meldingen
    `exclude` maakt het mogelijk om repos uit te sluiten van verwerking
    push geeft aan of er ook gepushed moet worden (working naar centraal, centraal naar bitbucket
    of github) en moet indien van toepassing expliciet als 'yes' worden opgegeven
    """
    def __init__(self, c, context='local', push=False, verbose=False, exclude=None):
        """set up variables for common use throughout the whole class
        instead op passing them around as function parameters
        """
        self.c = c
        if context not in ('local', 'remote'):
            raise ValueError('wrong context for this routine')
        self.context = context
        self.push = push
        self.verbose = verbose
        self.exclude = frozen_repos if exclude is None else exclude
        self.is_gitrepo = self.is_private = False

    def run(self):
        """main line; loop through selected repositories
        """
        outfile = REPOCHG if self.context == 'remote' else LOCALCHG
        changes = False
        with open(outfile, 'w') as _out:
            _out.write(f'check {self.context} repos on {TODAY}\n\n')
            for name in all_repos:
                if name in self.exclude:
                    continue
                self.is_gitrepo = name in git_repos
                self.is_private = name in private_repos
                pwd, root = self.get_locations(name)
                stats = []
                uncommitted, stats_append, writestuff = self.register_uncommitted(pwd)
                if stats_append:
                    stats.append(stats_append)
                if writestuff:
                    _out.write(writestuff)
                outgoing, stats_append, writestuff = self.register_outgoing(name, root, pwd)
                if stats_append:
                    stats.append(stats_append)
                if writestuff:
                    _out.write(writestuff)
                if stats:
                    print(' and '.join(stats) + f' for {name}')
                elif self.verbose:
                    print(f'no changes for {name}')
                if uncommitted or outgoing:
                    changes = True
                if outgoing and self.push:
                    writestuff = self.execute_push(name, root, pwd)
                    if writestuff:
                        _out.write(writestuff)
        print()
        if changes:
            print(f'for details see {outfile}')
        else:
            print('no change details')
        return changes

    def get_locations(self, name):
        """determine some key locations for the currrent repository
        """
        root = os.path.join(HOME, 'hg_repos') if self.context == 'remote' else HOME
        pwd = os.path.join(root, name)
        if self.context == 'remote':
            if self.is_gitrepo or self.is_private:
                pwd = os.path.join(root.replace('hg', 'git'), name)
                root = root.replace('hg', 'git')
        else:
            if self.is_private:
                pwd = os.path.join(root, private_repos[name])
            else:
                pwd = os.path.join(root, 'projects', name)
        return pwd, root

    def register_uncommitted(self, pwd):
        """check for uncommitted changes
        """
        uncommitted = False
        not_hg = self.is_gitrepo or self.is_private
        not_on_master = self.get_branchname(pwd) if not_hg else ''
        command = 'git status -uno --short' if not_hg else 'hg status --quiet'
        with self.c.cd(pwd):
            result = self.c.run(command, hide=True)
        test = result.stdout
        if test.strip():
            uncommitted = True
            on_branch = f' (on branch {not_on_master})' if not_on_master else ''
            stats_append = 'uncommitted changes' + on_branch
            writestuff = f'\nuncommitted changes in {pwd}{on_branch}\n'
            writestuff += test + '\n'
        else:
            stats_append, writestuff = '', ''
        return uncommitted, stats_append, writestuff

    def register_outgoing(self, name, root, pwd):
        """check for outgoing commits
        """
        outgoing = use_tipfile = False
        not_hg = self.is_gitrepo or self.is_private
        result = None
        if not_hg:
            command = 'git log origin/master..master'
        elif self.context == 'remote':
            tmpfile = os.path.join('/tmp', f'{name}_tip')
            tipfile = self.get_tipfilename(root, name)
            if not os.path.exists(tipfile):
                command = f'touch {tipfile}'
                self.c.run(command)
            command = 'hg tip'
            use_tipfile = True
        else:
            command = 'hg outgoing'
        if use_tipfile:
            with self.c.cd(pwd):
                self.c.run(f'{command} > {tmpfile}')
            with open(tmpfile) as _in1, open(tipfile) as _in2:
                buf1 = _in1.read()
                buf2 = _in2.read()
            outgoing = buf1 != buf2
        else:
            with self.c.cd(pwd):
                result = self.c.run(command, warn=True, hide=True)
                # print(result, result.ok, result.stdout, result.stderr)
                if not_hg:
                    outgoing = result.stdout.strip()
                else:
                    outgoing = result.ok
        if outgoing:
            stats_append = 'outgoing changes'
            writestuff = f'outgoing changes for {name}\n'
            if use_tipfile:
                writestuff += "-- local:\n"
                writestuff += buf1 + "\n"
                writestuff += "-- remote:\n"
                writestuff += buf2 + "\n"
            elif result:
                writestuff += result.stdout + '\n'
        else:
            stats_append, writestuff = '', ''
        return outgoing, stats_append, writestuff

    def execute_push(self, name, root, pwd):
        """"actually push the commit
        """
        not_hg = self.is_gitrepo or self.is_private
        if not_hg:
            ref = '-u' if self.context == 'remote' else ''
            command = f'git push {ref} origin master'
        else:
            command = 'hg push'
        with self.c.cd(pwd):
            result = self.c.run(command)
        if result.ok:
            writestuff = result.stdout + '\n'
            if not not_hg:
                if self.context == 'remote':
                    command = 'hg tip'
                    with self.c.cd(pwd):
                        self.c.run(f'{command} > {self.get_tipfilename(root, name)}')
                else:
                    command = 'hg up'
                    with self.c.cd(pwd):
                        result = self.c.run(command)
                        writestuff += result.stdout + '\n'
        else:
            writestuff = ''
        return writestuff

    def get_branchname(self, pwd):
        """find out which branch we're on
        """
        with self.c.cd(pwd):
            result = self.c.run('git branch', hide=True)
        name = ''
        for line in result.stdout.split('\n'):
            if line.startswith('*'):
                name = line.split()[1]
                break
        if name == 'master':
            return ''
        return name

    def get_tipfilename(self, root, name):
        """construct the name of the file we use to check if we need to push to remote
        (only for mercurial)"""
        return os.path.join(root, f'{name}_tip')


@task
def check_local(c):  # , dry_run=False):
    """compare all local repositories: working vs "central"
    """
    test = Check(c).run()   # , dry_run=dry_run)
    if test:
        print("use 'check-repo <reponame>' to inspect changes")
        print("    'binfab repo.check-local-notes` for remarks")


@task
def check_local_changes(c):
    "view output of check_local command"
    with c.cd('~/projects'):
        c.run(f'gnome-terminal --geometry=100x40 -- view {LOCALCHG}')


@task
def check_local_notes(c):
    "view remarks on repofiles not to be committed / pushed yet"
    with c.cd('~/projects'):
        # c.run("a-propos -n 'Ongoing stuff not needing to be committed yet' -f ongoing.apo &")
        c.run('treedocs projects.trd')


@task
def check_remote(c):   # , dry_run=False):
    """compare all hg repositories: "central" vs BitBucket / GitHub
    """
    Check(c, 'remote').run()  # , dry_run=dry_run)


@task(help={'exclude': 'comma separated list of repostories not to push'})
def push_local(c, exclude=None):  # , dry_run=False):
    """push all repos from working to "central" with possibility to exclude
    To exclude multiple repos you need to provide a string with escaped commas
    e.g. binfab push_remote
         binfab push remote:exclude=apropos
         binfab push_remote:exclude="apropos,albums"
    """
    Check(c, push=True, exclude=exclude).run()   # , dry_run=dry_run)


@task(help={'exclude': 'comma separated list of repostories not to push'})
def push_remote(c, exclude=None):   # , dry_run=False):
    """push all repos from "central" to BitBucket with possibility to exclude
    To exclude multiple repos you need to provide a string with escaped commas
    e.g. binfab push_remote
         binfab push remote:exclude=apropos
         binfab push_remote:exclude="apropos,albums"
    """
    Check(c, 'remote', push=True, exclude=exclude).run()  # , dry_run=dry_run)


@task(help={'names': 'comma separated list of repostories to push'})
def pushthru(c, names):
    """push from working to "central" and on to bitbucket if possible

    either name specific repos or check all
    when no name is specified, the "_check" variants are used
    """
    if not names:
        Check(c, push=True).run()
        Check(c, 'remote', push=True).run()
        with open(P2ULOG, 'w') as _out:
            for fname in (LOCALCHG, REPOCHG):
                with open(fname) as _in:
                    for line in _in:
                        _out.write(line)
        print('\nready, output in', P2ULOG)
        return
    print('niet uitgevoerd, moet herschreven worden o.a. naar gebruik van git')
    return
    errors = False
    with open(P2ULOG, 'w') as _out:
        for name in names.split(','):
            if name not in all_repos:
                # logline = '{} not pushed: is not on bitbucket'.format(name)
                logline = f'{name} not pushed: is not registered as a remote repo'
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
                logline = f'{name} - git outgoing check failed'
                _out.write(logline + "\n")
                _out.write(result.stderr + "\n")
                errors = True
            else:
                with c.cd(localpath):
                    # result = c.run('hg push --remotecmd update', warn=True, hide=True)
                    result = c.run('git push', warn=True, hide=True)
                _out.write(result.stdout + "\n")
                if result.failed:
                    logline = f'{name} - pushing failed'
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
                logline = f'{name} - pushing to github failed'
                _out.write(logline + "\n")
                _out.write(result.stderr + "\n")
                errors = True
    extra = ' with errors' if errors else ''
    print(f'ready{extra}, output in {P2ULOG}')


@task(help={'names': 'comma separated list of repostories to list',
            'outtype': 'format for output list - `csv` (default) or `txt`'})
def overview(c, names=None, outtype=''):
    """Try to build a history file from one or more repository logs
    meant to help me decide on tags or versions
    """
    # print('gemaakt voor oude hg repo, moet herschreven worden o.a. naar gebruik van git')
    # print('niet uitgevoerd, moet herschreven worden o.a. naar gebruik van git')
    # return
    outtype = outtype or 'csv'
    if outtype not in ('txt', 'csv'):
        print('wrong spec for output type')
        return
    root = get_project_root('bb')  # '/home/albert/hg_repos'
    # root = get_project_root('git')  # '/home/albert/git_repos'
    # root = get_project_root('local')  # '/home/albert/projects'
    if not names:
        names = list(os.listdir(root))
    else:
        names = names.split(',')
    for item in names:
        path = os.path.join(root, item)
        outdir = repo_overzicht(c, item, path, outtype)
    print(f'output in {outdir}')  # os.path.join(os.path.dirname(path), ".overzicht")))


def repo_overzicht(c, name, path, outtype):
    """Try to build a history file from a repository log
    currently it shows which commits contain which files
    """
    repotype = ''
    if not os.path.isdir(path):
        return ''
    if '.hg' in os.listdir(path):
        outdict = make_repolist_hg(c, path)
        repotype = 'hg'
    elif '.git' in os.listdir(path):
        outdict = make_repolist_git(c, path)
        repotype = 'git'
    else:
        return ''
    outdir = os.path.join(os.path.dirname(path), ".overzicht")
    if outtype == 'txt':
        outfile = os.path.join(outdir, f"{name}_repo.ovz")
        make_repo_ovz(outdict, outfile)
    elif outtype == 'csv':
        outfile = os.path.join(outdir, f"{name}_repo.csv")
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
    with c.cd(path):
        result = c.run('git log --pretty="%h; %ad; %s" --stat', hide=True)
        data = result.stdout
    outdict = collections.defaultdict(dict)
    key, date, desc, files = '', '', '', []
    for line in data.split('\n'):
        line = line.strip()
        if ';' in line:
            if key:
                outdict[key]['date'] = date
                outdict[key]['description'] = desc
                outdict[key]['files'] = files
            key, date, desc = line.split('; ')
            files = []
        elif '|' in line:
            file, rest = line.split('|')
            files.append(file.strip())
    if key:
        outdict[key]['date'] = date
        outdict[key]['description'] = desc
        outdict[key]['files'] = files
    return outdict


def make_repo_ovz(outdict, outfile):
    """write the history to a file

    input: history in the form of a dictionary, output filename
    output: the specified file as written to disk
    """
    with open(outfile, "w") as _out:
        for key in outdict.keys():
            _out.write('{}: {}\n'.format(outdict[key]['date'], '\n'.join(outdict[key]['desc'])))
            try:
                for item in outdict[key]['files']:
                    _out.write(f'    {item}\n')
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
            desc = f'"{desc}"'
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
def add2gitweb(c, name, frozen=False):
    "make a repository visible with gitweb"
    loc = '/.frozen' if frozen else ''
    c.run(f'sudo ln -s ~/git_repos{loc}/{name}/.git /var/lib/git/{name}.git')


def check_and_run_for_project(c, name, command):
    "run only if called for a valid project"
    if name:
        where = get_project_dir(name)
        if where:
            with c.cd(where):
                c.run(command)
        else:
            print(f'{name} is not a known project')
    else:
        where = os.getcwd()
        name = os.path.basename(where)
        if get_project_dir(name) == where:
            with c.cd(where):
                c.run(command)
        else:
            print('you are not in a known project directory')


@task(help={'name': 'repository name'})
def dtree(c, name=''):
    "Open project docs using treedocs, forcing qt mode"
    check_and_run_for_project(c, name, '~/projects/doctree/ensure-qt projdocs.trd')


@task(help={'name': 'repository name'})
def qgit(c, name=''):
    "Open Git gui after changing to repository"
    check_and_run_for_project(c, name, 'qgit')


@task
def mee_bezig(c):  # , name=''):
    "Open Doing list for a project using a-propos"
    # check_and_run_for_project(c, name, "a-propos -n 'Mee Bezig ({})' -f mee_bezig.apo".format(
    #     name or os.path.basename(os.getcwd())))
    c.run('treedocs ~/projects/projects.trd')


@task(help={'name': 'repository name'})
def preadme(c, name=''):
    "Open readme for project"
    check_and_run_for_project(c, name, 'pedit readme.rst')


@task(help={'name': 'repository name'})
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


@task(help={'find': 'text to find', 'rebuild': 'rebuild list of tracked files (default: False)'})
def search(c, find='', rebuild=False):
    "search in all tracked python files in all repos"
    if not os.path.exists(FILELIST) or rebuild:
        rebuild_filenamelist(c)
    command = f'afrift -m multi {FILELIST} -e py -P'
    if find:
        command += 'N -s ' + find
    c.run(command)


@task(help={'name': 'repository name', 'test': 'run tests for specific module, ? to list values'})
def runtests(c, name, test=''):
    "run all registered unittests for a project"
    check_and_run_for_project(c, name, 'run_unittests ' + test)
