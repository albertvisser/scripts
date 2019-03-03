"""Invoke ctags support stuff
"""
import os
from invoke import task
from repo import get_repofiles


@task(help={'names': 'comma-separated list of repos'})
def maketags(c, names):
    """build tags file for repository (by name or ".")
    """
    if not names:
        names = [x for x in all_repos]
    else:
        names = names.split(',')
    for name in names:
        path, files = get_repofiles(c, name)
        with c.cd(path):
            c.run('ctags -f .tags ' + ' '.join(files))


def check_changes(path, files):
    """compare time stamps of sources with .tags file
    """
    rebuild = False
    try:
        dts_tags = os.stat(os.path.join(path, '.tags')).st_mtime
    except OSError:
        return rebuild
    for fname in files:
        dts = os.stat(os.path.join(path, fname)).st_mtime
        if dts > dts_tags:
            rebuild = True
            break
    return rebuild


@task(help={'names': 'comma-separated list of repos'})
def checktags(c, names):
    """check if rebuilding tags file is necessary
    """
    if not names:
        names = [x for x in all_repos]
    else:
        names = names.split(',')
    for name in names:
        path, files = get_repofiles(c, name)
        if check_changes(path, files):
            print('.tags file rebuild needed for project', name)


@task(help={'names': 'comma-separated list of repos'})
def updatetags(c, names):
    """rebuild tags file for repository (by name or ".") if necessary
    """
    if not names:
        names = [x for x in all_repos]
    else:
        names = names.split(',')
    for name in names:
        path, files = get_repofiles(c, name)
        if _check_changes(path, files):
            print('rebuilding .tags file for project', name)
            with c.cd(path):
                c.run('ctags -f .tags ' + ' '.join(files))
