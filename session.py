"""Invoke commands for project/session/ticket management
"""
import os
import shutil
from invoke import task
from settings import PROJECTS_BASE, SESSIONS, DEVEL

@task(help={'name': 'name for new software project'})
def newproject(c, name):
    """start a new (Python) software project in a standardized way
    """
    loc = os.path.join(PROJECTS_BASE, name)
    if os.path.exists(loc):
        print('sorry, this project name is already in use')
        return
    shutil.copytree(os.path.join(PROJECTS_BASE, 'skeleton'), loc)
    os.rename(os.path.join(loc, 'projectname'), os.path.join(loc, name))
    tests_file = os.path.join(loc, 'tests', name + '_tests.py')
    os.rename(os.path.join(loc, 'tests', 'projectname_tests.py'), tests_file)
    with open(tests_file) as _in:
        data = _in.read()
    with open(tests_file, 'w') as _out:
        _out.write(data.replace('projectname', name))


@task(help={'name': 'name of session file'})
def start(c, name):
    """start a programming session using various tools

    expects a session script of the same name in .sessions (subdirectory for now)
    """
    fname = os.path.join(SESSIONS, name)
    c.run('/bin/sh {}'.format(fname))


@task(help={'name': 'name of session file'})
def edit(c, name):
    """define the tools to start a programming session with

    expects a session script of the same name in .sessions (subdirectory for now)
    each line contains a command to be executed
    """
    fname = os.path.join(SESSIONS, name)
    # c.run('scite {}'.format(fname))
    c.run('edit {}'.format(fname))


@task
def list(c):
    """list existing session names"""
    names = sorted('    {}'.format(x) for x in os.listdir(SESSIONS))
    print("available sessions:")
    print('\n'.join(names))


@task(help={'ticket': 'ticket number', 'project': 'project name'})
def ticket(c, ticket, project):
    """set up handling of a ticket for a given project

    clones the project repository and builds a session file
    """
    root = '_' + ticket
    with c.cd(DEVEL):
        c.run('hg clone {}/{} {}'.format(PROJECTS_BASE, project, root))
    dest = os.path.join(SESSIONS, ticket)
    settings = os.path.join(DEVEL, root, '.hg', 'hgrc')
    with open(settings) as _in:
        in_section = False
        for line in _in:
            if line.startswith('[paths]'):
                in_section = True
            elif in_section and line.startswith('default'):
                origin = line.split('=')[1].strip()
                break
        else:
            origin = ''
    if origin:
        origin = os.path.basename(origin)
        with open(dest, 'w') as _out:
            first = True
            with open(os.path.join(SESSIONS, origin)) as _in:
                for line in _in:
                    if line.startswith('cd ') and first:
                        line = 'cd {}\n'.format(os.path.join(DEVEL, root))
                        first = False
                    _out.write(line)
                _out.write("a-propos -n 'Mee Bezig' -f mee_bezig.pck &")


@task(help={'ticket': 'ticket number', 'project': 'project name'})
def prep(c, ticket, project):
    """check before pulling changes made for ticket into project

    """
    pull_dest = os.path.join(PROJECTS_BASE, project)
    pull_src = os.path.join(DEVEL, '_' + ticket)
    with c.cd(pull_dest):
        c.run('hg incoming {}'.format(pull_src))


@task(help={'ticket': 'ticket number', 'project': 'project name'})
def pull(c, ticket, project):
    """pull changes made for ticket into project

    """
    pull_dest = os.path.join(PROJECTS_BASE, project)
    pull_src = os.path.join(DEVEL, '_' + ticket)
    with c.cd(pull_dest):
        c.run('hg pull {}'.format(pull_src))
        c.run('hg up')


@task(help={'ticket': 'ticket number'})
def cleanup(c, ticket):
    """finish handling of a ticket by removing the repo clone and the session file
    """
    # remove session file
    os.remove(os.path.join(SESSIONS, ticket))
    # remove repository
    shutil.rmtree(os.path.join(DEVEL, '_' + ticket))
