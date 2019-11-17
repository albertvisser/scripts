"""Invoke routines for handling local and remote Mercurial and Git repositories
"""
import os
import os.path
import collections
import functools
import datetime
import csv
from invoke import task
from settings import PROJECTS_BASE, all_repos, git_repos, private_repos, sf_repos, \
    django_repos, cherrypy_repos
HOME = os.path.expanduser('~')
today = datetime.datetime.today()


def get_repofiles(c, reponame):
    """get all files from manifest
    """
    path = ''
    if reponame == '.':
        path = os.getcwd()
        reponame = os.path.basename(path)
    if reponame in all_repos:
        if not path:
            if reponame in private_repos:
                path = os.path.expanduser(os.path.join('~', reponame))
            elif reponame == 'bitbucket':
                path = os.path.expanduser(os.path.join('~', 'www', reponame))
            else:
                path = os.path.join(PROJECTS_BASE, reponame)
    else:
        print('not a code repository')
        return '', ''
    use_git = True if reponame in git_repos else False
    with c.cd(path):
        command = 'git ls-tree -r --name-only master' if use_git else 'hg manifest'
        result = c.run(command)
    files = [x for x in result.stdout.split('\n') if os.path.splitext(x)[1] == '.py']
    return path, files


def get_project_root(name, context='local'):
    """find out where a repository lives
    """
    # TODO: add site repositories like 'bitbucket'
    is_private = name in private_repos
    git_repo = name in git_repos
    sf_repo = name in sf_repos
    root = PROJECTS_BASE
    if context == 'local':
        if is_private:
            root = root.parent
    else:  # if context in ('remote', 'bb'):
        if is_private:
            root = root.parent / 'hg_private'
        elif git_repo and context not in ('sf', 'bb'):
            root = root.parent / 'git-repos'
        elif sf_repo and context == 'sf':
            root = root.parent / 'sf_repos'
        elif context not in ('git', 'sf'):
            root = root.parent / 'hg_repos'
    return root


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
        exclude = []
    local_ = context == 'local'
    remote = not local_
    if context not in ('local', 'remote'):
        print('wrong context for this routine')
        return ''
    elif local_:
        root, outfile = HOME, '/tmp/hg_local_changes'
    else:
        root, outfile = os.path.join(HOME, 'hg_repos'), '/tmp/hg_changes'

    changes = False
    with open(outfile, 'w') as _out:
        _out.write('check {} repos on {}\n\n'.format(context, today))
        for name in all_repos:
            if name in exclude:
                continue
            is_gitrepo = name in git_repos
            is_private = name in private_repos
            stats = []
            ## if context != 'local' and name in non_deploy_repos:  # non_bb_repos:
                ## continue
            pwd = os.path.join(root, name)
            if name == 'bitbucket':
                if remote:
                    pwd = os.path.join(root, 'avisser.bitbucket.org')
                else:
                    pwd = os.path.join(root, 'www', name)
            elif remote:
                if is_gitrepo or is_private:
                    pwd = os.path.join(root.replace('hg', 'git'), name)
                    root = root.replace('hg', 'git')
                # elif is_private:
                #     pwd = os.path.join(root.replace('repos', 'private'), name)
            elif local_ and not is_private:
                pwd = os.path.join(root, 'projects', name)

            ## tmp = '/tmp/hg_st_{}'.format(name)
            uncommitted = outgoing = False

            command = 'git status -uno --short' if (is_gitrepo or is_private) else 'hg status --quiet'
            if dry_run:
                print('execute `{}` in directory `{}`'.format(command, pwd))
            with c.cd(pwd):
                result = c.run(command, hide=True)
            test = result.stdout
            if test.strip():
                stats.append('uncommitted changes')
                _out.write('\nuncommitted changes in {}\n'.format(pwd))
                uncommitted = True
                _out.write(test + '\n')
            if remote:
                tmpfile = os.path.join('/tmp', '{}_tip'.format(name))
                tipfile = os.path.join(root, '{}_tip'.format(name))
                if not os.path.exists(tipfile):
                    command = 'touch {}'.format(tipfile)
                    if dry_run:
                        print('execute `{}`'.format(command))
                    c.run(command)

                command = 'git log -r -1' if is_gitrepo else 'hg tip'
                if dry_run:
                    print('execute `{}` in directory `{}`'.format(command, pwd))
                with c.cd(pwd):
                    c.run('{} > {}'.format(command, tmpfile))
                with open(tmpfile) as _in1, open(tipfile) as _in2:
                    buf1 = _in1.read()
                    buf2 = _in2.read()
                outgoing = buf1 != buf2
                if outgoing:
                    stats.append('outgoing changes')
                    _out.write('outgoing changes for {}\n'.format(name))
                    _out.write("--local:\n")
                    _out.write(buf1 + "\n")
                    _out.write("-- remote:\n")
                    _out.write(buf2 + "\n")
            else:
                command = 'git log --branches --not --remotes=origin' if is_gitrepo else 'hg outgoing'
                result = None
                if dry_run:
                    print('execute `{}` in directory `{}`'.format(command, pwd))
                with c.cd(pwd):
                    result = c.run(command, warn=True, hide=True)
                    # print(result, result.ok, result.stdout, result.stderr)
                    if is_gitrepo:
                        outgoing = result.stdout.strip()
                    else:
                        outgoing = result.ok
                if outgoing:
                    changes = True
                    stats.append('outgoing changes')
                    _out.write('\noutgoing changes for {}\n'.format(name))
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
            if is_gitrepo:
                ref = '-u' if remote else ''
                command = 'git push {} origin master'.format(ref)
            else:
                command = 'hg push'  # if bb else 'hg push --remotecmd "hg update"'
                # remotecmd werkt niet zo maar geen idee hoe dan wel
            if dry_run:
                print('execute `{}` in directory `{}`'.format(command, pwd))
            with c.cd(pwd):
                result = c.run(command)
            if result.ok:
                _out.write(result.stdout + '\n')
                if remote:
                    command = 'git log -r -1' if is_gitrepo else 'hg tip'
                    if dry_run:
                        print('execute `{}` in directory `{}`'.format(command, pwd))
                    with c.cd(pwd):
                        c.run('{} > {}'.format(command, tipfile))
                    # dropping sourcefroge support...
                    # if name in sf_repos:
                    #     sf_dir = pwd.replace('git_repos', 'sf-repos') + '-code'
                    #     if name == 'apropos':
                    #         sf_dir = sf_dir.replace('apropos', 'a-propos')
                    #     print('for sf push also from', sf_dir)
                    #     command = 'hg push'
                    #     with c.cd(sf_dir):
                    #         for comm in ('hg pull {}'.format(pwd), 'hg up', command):
                    #             result = c.run(comm)
                else:
                    with c.cd(pwd):
                        if not is_gitrepo:
                            result = c.run('hg up')
                            _out.write(result.stdout + '\n')

    print()
    if changes:
        print('for details see {}'.format(outfile))
    else:
        print('no change details')
    return changes


@task
def check_local(c):
    """compare all hg repositories: working vs "central"
    """
    test = _check(c)
    if test:
        print("use 'check-repo <reponame>' to inspect changes")


@task
def check_remote(c):
    """compare all hg repositories: "central" vs BitBucket / GitHub
    """
    _check(c, 'remote')


@task(help={'exclude': 'comma separated list of repostories not to push'})
def push_local(c, exclude=None):
    """push all repos from working to "central" with possibility to exclude
    To exclude multiple repos you need to provide a string with escaped commas
    e.g. binfab push_remote
         binfab push remote:exclude=apropos
         binfab push_remote:exclude="apropos,albums"
    """
    _check(c, push='yes', exclude=exclude)


@task(help={'exclude': 'comma separated list of repostories not to push'})
def push_remote(c, exclude=None):
    """push all repos from "central" to BitBucket with possibility to exclude
    To exclude multiple repos you need to provide a string with escaped commas
    e.g. binfab push_remote
         binfab push remote:exclude=apropos
         binfab push_remote:exclude="apropos,albums"
    """
    _check(c, 'remote', push='yes', exclude=exclude)


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
            for fname in ('/tmp/hg_local_changes', '/tmp/hg_changes'):
                with open(fname) as _in:
                    for line in _in:
                        _out.write(line)
        print('\nready, output in /tmp/pushthru_log')
        return
    errors = False
    with open('/tmp/pushthru_log', 'w') as _out:
        for name in names.split(','):
            if name not in all_repos:
                logline = '{} not pushed: is not on bitbucket'.format(name)
                print(logline)
                _out.write(logline + "\n")
                errors = True
                continue
            localpath = os.path.join('~', 'projects', name)
            centralpath = os.path.join('~', 'hg_repos', name)
            if name in private_repos:
                localpath = os.path.join('~', name)
                centralpath = centralpath.replace('repos', 'private')
            elif name in django_repos:
                localpath = localpath.replace('projects', os.path.join('www', 'django'))
            elif name in cherrypy_repos:
                localpath = localpath.replace('projects', os.path.join('www', 'cherrypy'))
            elif name == 'bitbucket':
                localpath = localpath.replace('projects', 'www')
                centralpath = centralpath.replace(name, 'avisser.bitbucket.org')
            with c.cd(localpath):
                result = c.run('hg outgoing', warn=True, hide=True)
            _out.write(result.stdout + "\n")
            if result.failed:
                logline = '{} - hg outgoing failed'.format(name)
                _out.write(logline + "\n")
                _out.write(result.stderr + "\n")
                errors = True
            else:
                with c.cd(localpath):
                    result = c.run('hg push --remotecmd update', warn=True, hide=True)
                _out.write(result.stdout + "\n")
                if result.failed:
                    logline = '{} - pushing failed'.format(name)
                    _out.write(logline + "\n")
                    _out.write(result.stderr + "\n")
                    errors = True
                    continue
            with c.cd(centralpath):
                result = c.run('hg push', warn=True, hide=True)
            _out.write(result.stdout + "\n")
            if result.failed:
                logline = '{} - pushing to bitbucket failed'.format(name)
                _out.write(logline + "\n")
                _out.write(result.stderr + "\n")
                errors = True
    extra = ' with errors' if errors else ''
    print('ready{}, output in /tmp/pushthru_log'.format(extra))


def _make_repolist(c, path):
    """turn the repo log into a history

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


def _repos_overzicht(c, name, path):
    """Try to build a history file from a repository log
    """
    if not os.path.isdir(path):
        return
    if '.hg' not in os.listdir(path):
        return
    # print('processing repository: {}'.format(name))
    outdict = _make_repolist(c, path)
    ## outfile = os.path.join(root, ".overzicht", "{}.repo_ovz".format(name))
    ## _make_repo_ovz(outdict, outfile)
    outfile = os.path.join(os.path.dirname(path), ".overzicht", "{}.csv".format(name))
    _make_repocsv(outdict, outfile)


@task(help={'names': 'comma separated list of repostories to list'})
def overview(c, names=None):
    """Try to build a history file from one or more repository logs
    meant to help me decide on tags or versions

    """
    root = '/home/albert/hg_repos'
    if not names:
        names = [x for x in os.listdir(root)]
    else:
        names = names.split(',')
    for item in names:
        path = os.path.join(root, item)
        _repos_overzicht(c, item, path)
    print('output in {}'.format(os.path.join(os.path.dirname(path), ".overzicht")))


@task(help={'name': 'repository name'})
def add2gitweb(c, name):
    "make a repository visible with gitweb"
    c.run('sudo ln -s ~/git_repos/{0}/.git /var/lib/git/{0}.git'.format(name))
