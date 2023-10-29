"""Invoke ctags support stuff
"""
import os
from invoke import task
from repo import get_repofiles
DEVEL = 'not used anymore'
from settings import all_repos


def list_repofiles(c, name):
    """get files from manifest from working or devel repo
    """
    if name in all_repos:
        path, files = get_repofiles(c, name)
    else:
        if name == '.':
            path = '.'
        else:
            path = os.path.join(DEVEL, '_' + name)
            if not os.path.exists(path):
                return None, None
        use_git = False
        if '.git' in os.listdir(path):
            use_git = True
        elif '.hg' not in os.listdir(path):
            return None, None
        with c.cd(path):
            command = 'git ls-tree -r --name-only master' if use_git else 'hg manifest'
            result = c.run(command, hide=True)
        files = [x for x in result.stdout.split('\n') if os.path.splitext(x)[1] == '.py']
    return path, files


@task(help={'names': 'comma-separated list of repos'})
def build(c, names):
    """build tags file for repository (by name or ".")
    """
    if not names:
        names = all_repos
    else:
        names = names.split(',')
    for name in names:
        path, files = list_repofiles(c, name)
        if path:
            with c.cd(path):
                c.run('ctags -f .tags ' + ' '.join(files))


def check_changes(path, files):
    """compare time stamps of sources with .tags file
    """
    rebuild = False
    try:
        dts_tags = os.stat(os.path.join(path, '.tags')).st_mtime
    except FileNotFoundError:  # OSError:
        print('no tags file found')
        return rebuild
    for fname in files:
        dts = os.stat(os.path.join(path, fname)).st_mtime
        if dts > dts_tags:
            rebuild = True
            break
    return rebuild


@task(help={'names': 'comma-separated list of repos'})
def check(c, names):
    """check if rebuilding tags file is necessary
    """
    if not names:
        names = all_repos
    else:
        names = names.split(',')
    for name in names:
        path, files = list_repofiles(c, name)
        if path:
            if check_changes(path, files):
                print('.tags file rebuild needed for project', name)


@task(help={'names': 'comma-separated list of repos'})
def update(c, names):
    """rebuild tags file for repository (by name or ".") if necessary
    """
    if not names:
        names = all_repos
    else:
        names = names.split(',')
    for name in names:
        path, files = list_repofiles(c, name)
        if path:
            if check_changes(path, files):
                print('rebuilding .tags file for project', name)
                with c.cd(path):
                    c.run('ctags -f .tags ' + ' '.join(files))
